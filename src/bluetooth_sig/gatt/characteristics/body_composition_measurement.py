"""Body Composition Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag
from typing import Any, ClassVar

import msgspec

from bluetooth_sig.types.units import MeasurementSystem, WeightUnit

from ..constants import PERCENTAGE_MAX, UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic, BodyCompositionFeatureData
from .utils import DataParser, IEEE11073Parser

BODY_FAT_PERCENTAGE_RESOLUTION = 0.1  # 0.1% resolution
MUSCLE_PERCENTAGE_RESOLUTION = 0.1  # 0.1% resolution
IMPEDANCE_RESOLUTION = 0.1  # 0.1 ohm resolution
MASS_RESOLUTION_KG = 0.005  # 0.005 kg resolution
MASS_RESOLUTION_LB = 0.01  # 0.01 lb resolution
HEIGHT_RESOLUTION_METRIC = 0.001  # 0.001 m resolution
HEIGHT_RESOLUTION_IMPERIAL = 0.1  # 0.1 inch resolution


class FlagsAndBodyFat(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Flags and body fat percentage with parsing offset."""

    flags: BodyCompositionFlags
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
    muscle_mass_unit: WeightUnit | None
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
    unit: WeightUnit


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
    measurement_units: MeasurementSystem
    timestamp: datetime | None = None
    user_id: int | None = None
    basal_metabolism: int | None = None
    muscle_mass: float | None = None
    muscle_mass_unit: WeightUnit | None = None
    muscle_percentage: float | None = None
    fat_free_mass: float | None = None
    soft_lean_mass: float | None = None
    body_water_mass: float | None = None
    impedance: float | None = None
    weight: float | None = None
    height: float | None = None

    def __post_init__(self) -> None:  # pylint: disable=too-many-branches
        """Validate body composition measurement data."""
        if not 0.0 <= self.body_fat_percentage <= PERCENTAGE_MAX:
            raise ValueError("Body fat percentage must be between 0-100%")
        if not 0 <= self.flags <= UINT16_MAX:
            raise ValueError("Flags must be a 16-bit value")

        # Validate measurement_units
        if not isinstance(self.measurement_units, MeasurementSystem):
            raise TypeError(f"Invalid measurement_units: {self.measurement_units!r}")

        # Validate mass fields units and ranges
        mass_fields = [
            ("muscle_mass", self.muscle_mass),
            ("fat_free_mass", self.fat_free_mass),
            ("soft_lean_mass", self.soft_lean_mass),
            ("body_water_mass", self.body_water_mass),
            ("weight", self.weight),
        ]
        for field_name, value in mass_fields:
            if value is not None and not value >= 0:
                raise ValueError(f"{field_name} must be non-negative")

        # Validate muscle_mass_unit consistency
        if self.muscle_mass is not None:
            expected_unit = WeightUnit.KG if self.measurement_units == MeasurementSystem.METRIC else WeightUnit.LB
            if self.muscle_mass_unit != expected_unit:
                raise ValueError(f"muscle_mass_unit must be {expected_unit!r}, got {self.muscle_mass_unit!r}")

        # Validate muscle_percentage
        if self.muscle_percentage is not None and not self.muscle_percentage >= 0:
            raise ValueError("Muscle percentage must be non-negative")

        # Validate impedance
        if self.impedance is not None and not self.impedance >= 0:
            raise ValueError("Impedance must be non-negative")

        # Validate height
        if self.height is not None and not self.height >= 0:
            raise ValueError("Height must be non-negative")

        # Validate basal_metabolism
        if self.basal_metabolism is not None and not self.basal_metabolism >= 0:
            raise ValueError("Basal metabolism must be non-negative")

        # Validate user_id
        if self.user_id is not None and not 0 <= self.user_id <= UINT8_MAX:
            raise ValueError(f"User ID must be 0-{UINT8_MAX}, got {self.user_id}")


class BodyCompositionMeasurementCharacteristic(BaseCharacteristic[BodyCompositionMeasurementData]):
    """Body Composition Measurement characteristic (0x2A9C).

    Used to transmit body composition measurement data including body
    fat percentage, muscle mass, bone mass, water percentage, and other
    body metrics.
    """

    _manual_unit: str = "various"  # Multiple units in measurement

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [BodyCompositionFeatureCharacteristic]

    min_length: int = 4  # Flags(2) + BodyFat(2) minimum
    max_length: int = 50  # + Timestamp(7) + UserID(1) + Multiple measurements maximum
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BodyCompositionMeasurementData:
        """Parse body composition measurement data according to Bluetooth specification.

        Format: Flags(2) + Body Fat %(2) + [Timestamp(7)] + [User ID(1)] +
                [Basal Metabolism(2)] + [Muscle Mass(2)] + [etc...]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to perform validation (currently unused).

        Returns:
            BodyCompositionMeasurementData containing parsed body composition data.

        Raises:
            ValueError: If data format is invalid.

        """
        # Parse flags and required body fat percentage
        header = self._parse_flags_and_body_fat(data)
        flags_enum = BodyCompositionFlags(header.flags)
        measurement_units = (
            MeasurementSystem.IMPERIAL
            if BodyCompositionFlags.IMPERIAL_UNITS in flags_enum
            else MeasurementSystem.METRIC
        )

        # Parse optional fields based on flags
        basic = self._parse_basic_optional_fields(data, flags_enum, header.offset)
        mass = self._parse_mass_fields(data, flags_enum, basic.offset)
        other = self._parse_other_measurements(data, flags_enum, mass.offset)

        # Validate against Body Composition Feature if context is available
        if ctx is not None:
            feature_value = self.get_context_characteristic(ctx, BodyCompositionFeatureCharacteristic)
            if feature_value is not None:
                self._validate_against_feature_characteristic(basic, mass, other, feature_value)

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

    def _encode_value(self, data: BodyCompositionMeasurementData) -> bytearray:
        """Encode body composition measurement value back to bytes.

        Args:
            data: BodyCompositionMeasurementData containing body composition measurement data

        Returns:
            Encoded bytes representing the measurement

        """
        result = bytearray()

        # Encode flags and body fat percentage
        self._encode_flags_and_body_fat(result, data)

        # Encode optional fields based on flags
        self._encode_optional_fields(result, data)

        return result

    def _encode_flags_and_body_fat(self, result: bytearray, data: BodyCompositionMeasurementData) -> None:
        """Encode flags and body fat percentage."""
        # Encode flags (16-bit)
        flags = int(data.flags)
        result.extend(DataParser.encode_int16(flags, signed=False))

        # Encode body fat percentage (uint16 with 0.1% resolution)
        body_fat_raw = round(data.body_fat_percentage / BODY_FAT_PERCENTAGE_RESOLUTION)
        if not 0 <= body_fat_raw <= UINT16_MAX:
            raise ValueError(f"Body fat percentage {body_fat_raw} exceeds uint16 range")
        result.extend(DataParser.encode_int16(body_fat_raw, signed=False))

    def _encode_optional_fields(self, result: bytearray, data: BodyCompositionMeasurementData) -> None:
        """Encode optional fields based on measurement data."""
        # Encode optional timestamp if present
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Encode optional user ID if present
        if data.user_id is not None:
            if not 0 <= data.user_id <= UINT8_MAX:
                raise ValueError(f"User ID {data.user_id} exceeds uint8 range")
            result.append(data.user_id)

        # Encode optional basal metabolism if present
        if data.basal_metabolism is not None:
            if not 0 <= data.basal_metabolism <= UINT16_MAX:
                raise ValueError(f"Basal metabolism {data.basal_metabolism} exceeds uint16 range")
            result.extend(DataParser.encode_int16(data.basal_metabolism, signed=False))

        # Encode mass-related fields
        self._encode_mass_fields(result, data)

        # Encode other measurements
        self._encode_other_measurements(result, data)

    def _encode_mass_fields(self, result: bytearray, data: BodyCompositionMeasurementData) -> None:
        """Encode mass-related optional fields."""
        # Encode optional muscle mass if present
        if data.muscle_mass is not None:
            mass_raw = round(data.muscle_mass / MASS_RESOLUTION_KG)
            if not 0 <= mass_raw <= UINT16_MAX:
                raise ValueError(f"Muscle mass raw value {mass_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(mass_raw, signed=False))

        # Encode optional muscle percentage if present
        if data.muscle_percentage is not None:
            muscle_pct_raw = round(data.muscle_percentage / MUSCLE_PERCENTAGE_RESOLUTION)
            if not 0 <= muscle_pct_raw <= UINT16_MAX:
                raise ValueError(f"Muscle percentage raw value {muscle_pct_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(muscle_pct_raw, signed=False))

        # Encode optional fat free mass if present
        if data.fat_free_mass is not None:
            mass_raw = round(data.fat_free_mass / MASS_RESOLUTION_KG)
            if not 0 <= mass_raw <= UINT16_MAX:
                raise ValueError(f"Fat free mass raw value {mass_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(mass_raw, signed=False))

        # Encode optional soft lean mass if present
        if data.soft_lean_mass is not None:
            mass_raw = round(data.soft_lean_mass / MASS_RESOLUTION_KG)
            if not 0 <= mass_raw <= UINT16_MAX:
                raise ValueError(f"Soft lean mass raw value {mass_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(mass_raw, signed=False))

        # Encode optional body water mass if present
        if data.body_water_mass is not None:
            mass_raw = round(data.body_water_mass / MASS_RESOLUTION_KG)
            if not 0 <= mass_raw <= UINT16_MAX:
                raise ValueError(f"Body water mass raw value {mass_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(mass_raw, signed=False))

    def _encode_other_measurements(self, result: bytearray, data: BodyCompositionMeasurementData) -> None:
        """Encode impedance, weight, and height measurements."""
        # Encode optional impedance if present
        if data.impedance is not None:
            impedance_raw = round(data.impedance / IMPEDANCE_RESOLUTION)
            if not 0 <= impedance_raw <= UINT16_MAX:
                raise ValueError(f"Impedance raw value {impedance_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(impedance_raw, signed=False))

        # Encode optional weight if present
        if data.weight is not None:
            mass_raw = round(data.weight / MASS_RESOLUTION_KG)
            if not 0 <= mass_raw <= UINT16_MAX:
                raise ValueError(f"Weight raw value {mass_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(mass_raw, signed=False))

        # Encode optional height if present
        if data.height is not None:
            if data.measurement_units == MeasurementSystem.IMPERIAL:
                height_raw = round(data.height / HEIGHT_RESOLUTION_IMPERIAL)  # 0.1 inch resolution
            else:
                height_raw = round(data.height / HEIGHT_RESOLUTION_METRIC)  # 0.001 m resolution
            if not 0 <= height_raw <= UINT16_MAX:
                raise ValueError(f"Height raw value {height_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(height_raw, signed=False))

    def _validate_against_feature_characteristic(
        self,
        basic: BasicOptionalFields,
        mass: MassFields,
        other: OtherMeasurements,
        feature_data: BodyCompositionFeatureData,
    ) -> None:
        """Validate measurement data against Body Composition Feature characteristic.

        Args:
            basic: Basic optional fields (timestamp, user_id, basal_metabolism)
            mass: Mass-related fields
            other: Other measurements (impedance, weight, height)
            feature_data: BodyCompositionFeatureData from feature characteristic

        Raises:
            ValueError: If measurement reports unsupported features

        """
        # Check that reported measurements are supported by device features
        if basic.timestamp is not None and not feature_data.timestamp_supported:
            raise ValueError("Timestamp reported but not supported by device features")

        if basic.user_id is not None and not feature_data.multiple_users_supported:
            raise ValueError("User ID reported but not supported by device features")

        if basic.basal_metabolism is not None and not feature_data.basal_metabolism_supported:
            raise ValueError("Basal metabolism reported but not supported by device features")

        if mass.muscle_mass is not None and not feature_data.muscle_mass_supported:
            raise ValueError("Muscle mass reported but not supported by device features")

        if mass.muscle_percentage is not None and not feature_data.muscle_percentage_supported:
            raise ValueError("Muscle percentage reported but not supported by device features")

        if mass.fat_free_mass is not None and not feature_data.fat_free_mass_supported:
            raise ValueError("Fat free mass reported but not supported by device features")

        if mass.soft_lean_mass is not None and not feature_data.soft_lean_mass_supported:
            raise ValueError("Soft lean mass reported but not supported by device features")

        if mass.body_water_mass is not None and not feature_data.body_water_mass_supported:
            raise ValueError("Body water mass reported but not supported by device features")

        if other.impedance is not None and not feature_data.impedance_supported:
            raise ValueError("Impedance reported but not supported by device features")

        if other.weight is not None and not feature_data.weight_supported:
            raise ValueError("Weight reported but not supported by device features")

        if other.height is not None and not feature_data.height_supported:
            raise ValueError("Height reported but not supported by device features")

    def _parse_flags_and_body_fat(self, data: bytearray) -> FlagsAndBodyFat:
        """Parse flags and body fat percentage from data.

        Returns:
            FlagsAndBodyFat containing flags, body fat percentage, and offset

        """
        # Parse flags (2 bytes)
        flags = BodyCompositionFlags(DataParser.parse_int16(data, 0, signed=False))

        # Validate and parse body fat percentage data

        body_fat_raw = DataParser.parse_int16(data, 2, signed=False)
        body_fat_percentage = float(body_fat_raw) * BODY_FAT_PERCENTAGE_RESOLUTION  # 0.1% resolution

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
        muscle_mass_unit: WeightUnit | None = None
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
            muscle_percentage = muscle_percentage_raw * MUSCLE_PERCENTAGE_RESOLUTION
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
            impedance = impedance_raw * IMPEDANCE_RESOLUTION
            offset += 2

        # Parse optional weight
        if BodyCompositionFlags.WEIGHT_PRESENT in flags and len(data) >= offset + 2:
            weight = self._parse_mass_field(data, flags, offset).value
            offset += 2

        # Parse optional height
        if BodyCompositionFlags.HEIGHT_PRESENT in flags and len(data) >= offset + 2:
            height_raw = DataParser.parse_int16(data, offset, signed=False)
            if BodyCompositionFlags.IMPERIAL_UNITS in flags:  # Imperial units
                height = height_raw * HEIGHT_RESOLUTION_IMPERIAL  # 0.1 inch resolution
            else:  # SI units
                height = height_raw * HEIGHT_RESOLUTION_METRIC  # 0.001 m resolution
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
            mass = mass_raw * MASS_RESOLUTION_LB  # 0.01 lb resolution
            mass_unit = WeightUnit.LB
        else:  # SI units
            mass = mass_raw * MASS_RESOLUTION_KG  # 0.005 kg resolution
            mass_unit = WeightUnit.KG
        return MassValue(value=mass, unit=mass_unit)
