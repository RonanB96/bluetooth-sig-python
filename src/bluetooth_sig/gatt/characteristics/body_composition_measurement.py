"""Body Composition Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from ..constants import PERCENTAGE_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# TODO: Implement CharacteristicContext support
# This characteristic should access Body Composition Feature (0x2A9B) from ctx.other_characteristics
# to determine which optional fields are supported and apply appropriate scaling factors


class FlagsAndBodyFat(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Flags and body fat percentage with parsing offset."""

    flags: int
    body_fat_percentage: float
    offset: int


class BasicOptionalFields(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Basic optional fields: timestamp, user ID, and basal metabolism."""

    timestamp: datetime | None
    user_id: int | None
    basal_metabolism: int | None
    offset: int


class MassFields(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Mass-related optional fields."""

    muscle_mass: float | None
    muscle_mass_unit: str | None
    muscle_percentage: float | None
    fat_free_mass: float | None
    soft_lean_mass: float | None
    body_water_mass: float | None
    offset: int


class OtherMeasurements(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Impedance, weight, and height measurements."""

    impedance: float | None
    weight: float | None
    height: float | None


class MassValue(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Single mass field with unit."""

    value: float
    unit: str


class BodyCompositionFlags(IntFlag):
    """Body Composition Measurement flags as per Bluetooth SIG specification."""

    IMPERIAL_UNITS = 0x001
    TIMESTAMP_PRESENT = 0x002
    USER_ID_PRESENT = 0x004
    BASAL_METABOLISM_PRESENT = 0x008
    MUSCLE_MASS_PRESENT = 0x010
    MUSCLE_PERCENTAGE_PRESENT = 0x020
    FAT_FREE_MASS_PRESENT = 0x040
    SOFT_LEAN_MASS_PRESENT = 0x080
    BODY_WATER_MASS_PRESENT = 0x100
    IMPEDANCE_PRESENT = 0x200
    WEIGHT_PRESENT = 0x400
    HEIGHT_PRESENT = 0x800


class BodyCompositionMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Body Composition Measurement characteristic."""

    body_fat_percentage: float
    flags: BodyCompositionFlags
    measurement_units: str
    timestamp: datetime | None = None
    user_id: int | None = None
    basal_metabolism: int | None = None
    muscle_mass: float | None = None
    muscle_mass_unit: str | None = None  # Added missing field
    muscle_percentage: float | None = None
    fat_free_mass: float | None = None
    soft_lean_mass: float | None = None
    body_water_mass: float | None = None
    impedance: float | None = None
    weight: float | None = None
    height: float | None = None

    def __post_init__(self) -> None:
        """Validate body composition measurement data."""
        if not 0.0 <= self.body_fat_percentage <= PERCENTAGE_MAX:
            raise ValueError("Body fat percentage must be between 0-100%")
        if not 0 <= self.flags <= 0xFFFF:
            raise ValueError("Flags must be a 16-bit value")


class BodyCompositionMeasurementCharacteristic(BaseCharacteristic):
    """Body Composition Measurement characteristic (0x2A9C).

    Used to transmit body composition measurement data including body
    fat percentage, muscle mass, bone mass, water percentage, and other
    body metrics.
    """

    _manual_unit: str = "various"  # Multiple units in measurement

    min_length: int = 4  # Flags(2) + BodyFat(2) minimum
    max_length: int = 50  # + Timestamp(7) + UserID(1) + Multiple measurements maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BodyCompositionMeasurementData:
        """Parse body composition measurement data according to Bluetooth specification.

        Format: Flags(2) + Body Fat %(2) + [Timestamp(7)] + [User ID(1)] +
                [Basal Metabolism(2)] + [Muscle Mass(2)] + [etc...]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            BodyCompositionMeasurementData containing parsed body composition data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 4:
            raise ValueError("Body Composition Measurement data must be at least 4 bytes")

        # Parse flags and required body fat percentage
        header = self._parse_flags_and_body_fat(data)
        flags_enum = BodyCompositionFlags(header.flags)
        measurement_units = "imperial" if BodyCompositionFlags.IMPERIAL_UNITS in flags_enum else "metric"

        # Parse optional fields based on flags
        basic = self._parse_basic_optional_fields(data, flags_enum, header.offset)
        mass = self._parse_mass_fields(data, flags_enum, basic.offset)
        other = self._parse_other_measurements(data, flags_enum, mass.offset)

        # Create struct with all parsed values
        return BodyCompositionMeasurementData(
            body_fat_percentage=header.body_fat_percentage,
            flags=flags_enum,
            measurement_units=measurement_units,
            timestamp=basic.timestamp,
            user_id=basic.user_id,
            basal_metabolism=basic.basal_metabolism,
            muscle_mass=mass.muscle_mass,
            muscle_mass_unit=mass.muscle_mass_unit,
            muscle_percentage=mass.muscle_percentage,
            fat_free_mass=mass.fat_free_mass,
            soft_lean_mass=mass.soft_lean_mass,
            body_water_mass=mass.body_water_mass,
            impedance=other.impedance,
            weight=other.weight,
            height=other.height,
        )

    def encode_value(self, data: BodyCompositionMeasurementData) -> bytearray:
        """Encode body composition measurement value back to bytes.

        Args:
            data: BodyCompositionMeasurementData containing body composition measurement data

        Returns:
            Encoded bytes representing the measurement (simplified implementation)

        """
        # This is a complex characteristic with many optional fields
        # Implementing a basic version that handles the core data
        flags = data.flags
        body_fat_percentage = data.body_fat_percentage

        # Build basic result with flags and body fat percentage
        result = bytearray()
        result.extend(DataParser.encode_int16(int(flags), signed=False))  # Flags (16-bit)

        # Convert body fat percentage to uint16 with 0.1% resolution
        body_fat_raw = round(body_fat_percentage * 10)
        if not 0 <= body_fat_raw <= 0xFFFF:
            raise ValueError(f"Body fat percentage {body_fat_raw} exceeds uint16 range")
        result.extend(DataParser.encode_int16(body_fat_raw, signed=False))

        # Additional fields would be added based on flags (simplified)
        return result

    def _parse_flags_and_body_fat(self, data: bytearray) -> FlagsAndBodyFat:
        """Parse flags and body fat percentage from data.

        Returns:
            FlagsAndBodyFat containing flags, body fat percentage, and offset

        """
        # Parse flags (2 bytes)
        flags = DataParser.parse_int16(data, 0, signed=False)

        # Validate and parse body fat percentage data
        if len(data) < 4:
            raise ValueError("Insufficient data for body fat percentage")

        body_fat_raw = DataParser.parse_int16(data, 2, signed=False)
        body_fat_percentage = float(body_fat_raw) * 0.1  # 0.1% resolution

        return FlagsAndBodyFat(flags=flags, body_fat_percentage=body_fat_percentage, offset=4)

    def _parse_basic_optional_fields(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
    ) -> BasicOptionalFields:
        """Parse basic optional fields (timestamp, user ID, basal metabolism).

        Args:
            data: Raw bytearray
            flags: Parsed flags indicating which fields are present
            offset: Current offset in data

        Returns:
            BasicOptionalFields containing timestamp, user_id, basal_metabolism, and updated offset

        """
        timestamp: datetime | None = None
        user_id: int | None = None
        basal_metabolism: int | None = None

        # Parse optional timestamp (7 bytes) if present
        if BodyCompositionFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional user ID (1 byte) if present
        if BodyCompositionFlags.USER_ID_PRESENT in flags and len(data) >= offset + 1:
            user_id = int(data[offset])
            offset += 1

        # Parse optional basal metabolism (uint16) if present
        if BodyCompositionFlags.BASAL_METABOLISM_PRESENT in flags and len(data) >= offset + 2:
            basal_metabolism_raw = DataParser.parse_int16(data, offset, signed=False)
            basal_metabolism = basal_metabolism_raw  # in kJ
            offset += 2

        return BasicOptionalFields(
            timestamp=timestamp, user_id=user_id, basal_metabolism=basal_metabolism, offset=offset
        )

    def _parse_mass_fields(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
    ) -> MassFields:
        """Parse mass-related optional fields.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset

        Returns:
            MassFields containing muscle_mass, muscle_mass_unit, muscle_percentage,
            fat_free_mass, soft_lean_mass, body_water_mass, and updated offset

        """
        muscle_mass: float | None = None
        muscle_mass_unit: str | None = None
        muscle_percentage: float | None = None
        fat_free_mass: float | None = None
        soft_lean_mass: float | None = None
        body_water_mass: float | None = None

        # Parse optional muscle mass
        if BodyCompositionFlags.MUSCLE_MASS_PRESENT in flags and len(data) >= offset + 2:
            mass_value = self._parse_mass_field(data, flags, offset)
            muscle_mass = mass_value.value
            muscle_mass_unit = mass_value.unit
            offset += 2

        # Parse optional muscle percentage
        if BodyCompositionFlags.MUSCLE_PERCENTAGE_PRESENT in flags and len(data) >= offset + 2:
            muscle_percentage_raw = DataParser.parse_int16(data, offset, signed=False)
            muscle_percentage = muscle_percentage_raw * 0.1
            offset += 2

        # Parse optional fat free mass
        if BodyCompositionFlags.FAT_FREE_MASS_PRESENT in flags and len(data) >= offset + 2:
            fat_free_mass = self._parse_mass_field(data, flags, offset).value
            offset += 2

        # Parse optional soft lean mass
        if BodyCompositionFlags.SOFT_LEAN_MASS_PRESENT in flags and len(data) >= offset + 2:
            soft_lean_mass = self._parse_mass_field(data, flags, offset).value
            offset += 2

        # Parse optional body water mass
        if BodyCompositionFlags.BODY_WATER_MASS_PRESENT in flags and len(data) >= offset + 2:
            body_water_mass = self._parse_mass_field(data, flags, offset).value
            offset += 2

        return MassFields(
            muscle_mass=muscle_mass,
            muscle_mass_unit=muscle_mass_unit,
            muscle_percentage=muscle_percentage,
            fat_free_mass=fat_free_mass,
            soft_lean_mass=soft_lean_mass,
            body_water_mass=body_water_mass,
            offset=offset,
        )

    def _parse_other_measurements(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
    ) -> OtherMeasurements:
        """Parse impedance, weight, and height measurements.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset

        Returns:
            OtherMeasurements containing impedance, weight, and height

        """
        impedance: float | None = None
        weight: float | None = None
        height: float | None = None

        # Parse optional impedance
        if BodyCompositionFlags.IMPEDANCE_PRESENT in flags and len(data) >= offset + 2:
            impedance_raw = DataParser.parse_int16(data, offset, signed=False)
            impedance = impedance_raw * 0.1
            offset += 2

        # Parse optional weight
        if BodyCompositionFlags.WEIGHT_PRESENT in flags and len(data) >= offset + 2:
            weight = self._parse_mass_field(data, flags, offset).value
            offset += 2

        # Parse optional height
        if BodyCompositionFlags.HEIGHT_PRESENT in flags and len(data) >= offset + 2:
            height_raw = DataParser.parse_int16(data, offset, signed=False)
            if BodyCompositionFlags.IMPERIAL_UNITS in flags:  # Imperial units
                height = height_raw * 0.1  # 0.1 inch resolution
            else:  # SI units
                height = height_raw * 0.001  # 0.001 m resolution
            offset += 2

        return OtherMeasurements(impedance=impedance, weight=weight, height=height)

    def _parse_mass_field(self, data: bytearray, flags: BodyCompositionFlags, offset: int) -> MassValue:
        """Parse a mass field with unit conversion.

        Args:
            data: Raw bytearray
            flags: Parsed flags for unit determination
            offset: Current offset

        Returns:
            MassValue containing mass value and unit string

        """
        mass_raw = DataParser.parse_int16(data, offset, signed=False)
        if BodyCompositionFlags.IMPERIAL_UNITS in flags:  # Imperial units
            mass = mass_raw * 0.01  # 0.01 lb resolution
            mass_unit = "lb"
        else:  # SI units
            mass = mass_raw * 0.005  # 0.005 kg resolution
            mass_unit = "kg"
        return MassValue(value=mass, unit=mass_unit)
