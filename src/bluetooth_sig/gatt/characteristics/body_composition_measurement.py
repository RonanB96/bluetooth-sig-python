"""Body Composition Measurement characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntFlag
from typing import Any

from ..constants import PERCENTAGE_MAX
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# TODO: Implement CharacteristicContext support
# This characteristic should access Body Composition Feature (0x2A9B) from ctx.other_characteristics
# to determine which optional fields are supported and apply appropriate scaling factors


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


@dataclass
class BodyCompositionMeasurementData:  # pylint: disable=too-many-instance-attributes # Comprehensive medical measurement data with many optional fields
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


@dataclass
class BodyCompositionMeasurementCharacteristic(BaseCharacteristic):
    """Body Composition Measurement characteristic (0x2A9C).

    Used to transmit body composition measurement data including body fat percentage,
    muscle mass, bone mass, water percentage, and other body metrics.
    """

    _characteristic_name: str = "Body Composition Measurement"

    min_length: int = 4  # Flags(2) + BodyFat(2) minimum
    max_length: int = 50  # + Timestamp(7) + UserID(1) + Multiple measurements maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(
        self, data: bytearray, ctx: Any | None = None
    ) -> BodyCompositionMeasurementData:
        """Parse body composition measurement data according to Bluetooth specification.

        Format: Flags(2) + Body Fat %(2) + [Timestamp(7)] + [User ID(1)] +
                [Basal Metabolism(2)] + [Muscle Mass(2)] + [etc...]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            BodyCompositionMeasurementData containing parsed body composition data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError(
                "Body Composition Measurement data must be at least 4 bytes"
            )

        # Parse flags and required body fat percentage
        flags, offset = self._parse_flags_and_body_fat(data)

        # Create dataclass with required fields
        result = BodyCompositionMeasurementData(
            body_fat_percentage=self._calculate_body_fat_percentage(data, offset - 2),
            flags=BodyCompositionFlags(flags),
            measurement_units="imperial"
            if BodyCompositionFlags.IMPERIAL_UNITS in BodyCompositionFlags(flags)
            else "metric",
        )

        # Parse optional fields based on flags
        self._parse_optional_fields(data, result.flags, offset, result)

        return result

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
        result.extend(
            DataParser.encode_int16(int(flags), signed=False)
        )  # Flags (16-bit)

        # Convert body fat percentage to uint16 with 0.1% resolution
        body_fat_raw = round(body_fat_percentage * 10)
        if not 0 <= body_fat_raw <= 0xFFFF:
            raise ValueError(f"Body fat percentage {body_fat_raw} exceeds uint16 range")
        result.extend(DataParser.encode_int16(body_fat_raw, signed=False))

        # Additional fields would be added based on flags (simplified)
        return result

    def _parse_flags_and_body_fat(self, data: bytearray) -> tuple[int, int]:
        """Parse flags and body fat percentage from data.

        Returns:
            tuple: (flags, offset_after_body_fat)
        """
        # Parse flags (2 bytes)
        flags = DataParser.parse_int16(data, 0, signed=False)
        offset = 2

        # Validate body fat percentage data is present
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for body fat percentage")

        return flags, offset + 2

    def _calculate_body_fat_percentage(self, data: bytearray, offset: int) -> float:
        """Calculate body fat percentage from raw data.

        Args:
            data: Raw bytearray
            offset: Offset to body fat data

        Returns:
            Body fat percentage as float
        """
        body_fat_raw = DataParser.parse_int16(data, offset, signed=False)
        return float(body_fat_raw) * 0.1  # 0.1% resolution

    def _parse_optional_fields(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
        result: BodyCompositionMeasurementData,
    ) -> None:
        """Parse all optional fields based on flags.

        Args:
            data: Raw bytearray
            flags: Parsed flags indicating which fields are present
            offset: Current offset in data
            result: Result dataclass to populate
        """
        # Parse optional timestamp (7 bytes) if present
        if BodyCompositionFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            result.timestamp = timestamp
            offset += 7

        # Parse optional user ID (1 byte) if present
        if BodyCompositionFlags.USER_ID_PRESENT in flags and len(data) >= offset + 1:
            result.user_id = data[offset]
            offset += 1

        # Parse optional basal metabolism (uint16) if present
        if (
            BodyCompositionFlags.BASAL_METABOLISM_PRESENT in flags
            and len(data) >= offset + 2
        ):
            basal_metabolism_raw = DataParser.parse_int16(data, offset, signed=False)
            result.basal_metabolism = basal_metabolism_raw  # in kJ
            offset += 2

        # Parse mass-related fields
        offset = self._parse_mass_fields(data, flags, offset, result)

        # Parse other measurement fields
        self._parse_other_measurements(data, flags, offset, result)

    def _parse_mass_fields(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
        result: BodyCompositionMeasurementData,
    ) -> int:
        """Parse mass-related optional fields.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset
            result: Result dataclass to populate

        Returns:
            Updated offset
        """
        # Parse optional muscle mass
        if (
            BodyCompositionFlags.MUSCLE_MASS_PRESENT in flags
            and len(data) >= offset + 2
        ):
            muscle_mass, mass_unit = self._parse_mass_field(data, flags, offset)
            result.muscle_mass = muscle_mass
            result.muscle_mass_unit = mass_unit
            offset += 2

        # Parse optional muscle percentage
        if (
            BodyCompositionFlags.MUSCLE_PERCENTAGE_PRESENT in flags
            and len(data) >= offset + 2
        ):
            muscle_percentage_raw = DataParser.parse_int16(data, offset, signed=False)
            result.muscle_percentage = muscle_percentage_raw * 0.1
            offset += 2

        # Parse optional fat free mass
        if (
            BodyCompositionFlags.FAT_FREE_MASS_PRESENT in flags
            and len(data) >= offset + 2
        ):
            fat_free_mass, _ = self._parse_mass_field(data, flags, offset)
            result.fat_free_mass = fat_free_mass
            offset += 2

        # Parse optional soft lean mass
        if (
            BodyCompositionFlags.SOFT_LEAN_MASS_PRESENT in flags
            and len(data) >= offset + 2
        ):
            soft_lean_mass, _ = self._parse_mass_field(data, flags, offset)
            result.soft_lean_mass = soft_lean_mass
            offset += 2

        # Parse optional body water mass
        if (
            BodyCompositionFlags.BODY_WATER_MASS_PRESENT in flags
            and len(data) >= offset + 2
        ):
            body_water_mass, _ = self._parse_mass_field(data, flags, offset)
            result.body_water_mass = body_water_mass
            offset += 2

        return offset

    def _parse_other_measurements(
        self,
        data: bytearray,
        flags: BodyCompositionFlags,
        offset: int,
        result: BodyCompositionMeasurementData,
    ) -> None:
        """Parse impedance, weight, and height measurements.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset
            result: Result dataclass to populate
        """
        # Parse optional impedance
        if BodyCompositionFlags.IMPEDANCE_PRESENT in flags and len(data) >= offset + 2:
            impedance_raw = DataParser.parse_int16(data, offset, signed=False)
            result.impedance = impedance_raw * 0.1
            offset += 2

        # Parse optional weight
        if BodyCompositionFlags.WEIGHT_PRESENT in flags and len(data) >= offset + 2:
            weight, _ = self._parse_mass_field(data, flags, offset)
            result.weight = weight
            offset += 2

        # Parse optional height
        if BodyCompositionFlags.HEIGHT_PRESENT in flags and len(data) >= offset + 2:
            height_raw = DataParser.parse_int16(data, offset, signed=False)
            if BodyCompositionFlags.IMPERIAL_UNITS in flags:  # Imperial units
                height = height_raw * 0.1  # 0.1 inch resolution
            else:  # SI units
                height = height_raw * 0.001  # 0.001 m resolution
            result.height = height
            offset += 2

    def _parse_mass_field(
        self, data: bytearray, flags: BodyCompositionFlags, offset: int
    ) -> tuple[float, str]:
        """Parse a mass field with unit conversion.

        Args:
            data: Raw bytearray
            flags: Parsed flags for unit determination
            offset: Current offset

        Returns:
            tuple: (mass_value, unit_string)
        """
        mass_raw = DataParser.parse_int16(data, offset, signed=False)
        if BodyCompositionFlags.IMPERIAL_UNITS in flags:  # Imperial units
            mass = mass_raw * 0.01  # 0.01 lb resolution
            mass_unit = "lb"
        else:  # SI units
            mass = mass_raw * 0.005  # 0.005 kg resolution
            mass_unit = "kg"
        return mass, mass_unit
