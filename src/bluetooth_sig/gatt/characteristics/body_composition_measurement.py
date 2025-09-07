"""Body Composition Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class BodyCompositionMeasurementCharacteristic(BaseCharacteristic):
    """Body Composition Measurement characteristic (0x2A9C).

    Used to transmit body composition measurement data including body fat percentage,
    muscle mass, bone mass, water percentage, and other body metrics.
    """

    _characteristic_name: str = "Body Composition Measurement"

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse body composition measurement data according to Bluetooth specification.

        Format: Flags(2) + Body Fat %(2) + [Timestamp(7)] + [User ID(1)] +
                [Basal Metabolism(2)] + [Muscle Mass(2)] + [etc...]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed body composition data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError(
                "Body Composition Measurement data must be at least 4 bytes"
            )

        # Parse flags and required body fat percentage
        flags, offset = self._parse_flags_and_body_fat(data)

        result = {
            "body_fat_percentage": self._calculate_body_fat_percentage(
                data, offset - 2
            ),
            "flags": flags,
            "measurement_units": "imperial" if (flags & 0x01) else "metric",
        }

        # Parse optional fields based on flags
        offset = self._parse_optional_fields(data, flags, offset, result)

        return result


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    def _parse_flags_and_body_fat(self, data: bytearray) -> tuple[int, int]:
        """Parse flags and body fat percentage from data.

        Returns:
            tuple: (flags, offset_after_body_fat)
        """
        # Parse flags (2 bytes)
        flags = struct.unpack("<H", data[:2])[0]
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
        body_fat_raw = struct.unpack("<H", data[offset : offset + 2])[0]
        return body_fat_raw * 0.1  # 0.1% resolution

    def _parse_optional_fields(
        self, data: bytearray, flags: int, offset: int, result: dict[str, Any]
    ) -> int:
        """Parse all optional fields based on flags.

        Args:
            data: Raw bytearray
            flags: Parsed flags indicating which fields are present
            offset: Current offset in data
            result: Result dictionary to populate

        Returns:
            Final offset after parsing all fields
        """
        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 7:
            timestamp = self._parse_ieee11073_timestamp(data, offset)
            result["timestamp"] = timestamp
            offset += 7

        # Parse optional user ID (1 byte) if present
        if (flags & 0x04) and len(data) >= offset + 1:
            result["user_id"] = data[offset]
            offset += 1

        # Parse optional basal metabolism (uint16) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            basal_metabolism_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["basal_metabolism"] = basal_metabolism_raw  # in kJ
            result["basal_metabolism_unit"] = "kJ"
            offset += 2

        # Parse mass-related fields
        offset = self._parse_mass_fields(data, flags, offset, result)

        # Parse other measurement fields
        offset = self._parse_other_measurements(data, flags, offset, result)

        return offset

    def _parse_mass_fields(
        self, data: bytearray, flags: int, offset: int, result: dict[str, Any]
    ) -> int:
        """Parse mass-related optional fields.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset
            result: Result dictionary to populate

        Returns:
            Updated offset
        """
        # Parse optional muscle mass
        if (flags & 0x10) and len(data) >= offset + 2:
            muscle_mass, mass_unit = self._parse_mass_field(data, flags, offset)
            result["muscle_mass"] = muscle_mass
            result["muscle_mass_unit"] = mass_unit
            offset += 2

        # Parse optional muscle percentage
        if (flags & 0x20) and len(data) >= offset + 2:
            muscle_percentage_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["muscle_percentage"] = muscle_percentage_raw * 0.1
            offset += 2

        # Parse optional fat free mass
        if (flags & 0x40) and len(data) >= offset + 2:
            fat_free_mass, mass_unit = self._parse_mass_field(data, flags, offset)
            result["fat_free_mass"] = fat_free_mass
            result["fat_free_mass_unit"] = mass_unit
            offset += 2

        # Parse optional soft lean mass
        if (flags & 0x80) and len(data) >= offset + 2:
            soft_lean_mass, mass_unit = self._parse_mass_field(data, flags, offset)
            result["soft_lean_mass"] = soft_lean_mass
            result["soft_lean_mass_unit"] = mass_unit
            offset += 2

        # Parse optional body water mass
        if (flags & 0x100) and len(data) >= offset + 2:
            body_water_mass, mass_unit = self._parse_mass_field(data, flags, offset)
            result["body_water_mass"] = body_water_mass
            result["body_water_mass_unit"] = mass_unit
            offset += 2

        return offset

    def _parse_other_measurements(
        self, data: bytearray, flags: int, offset: int, result: dict[str, Any]
    ) -> int:
        """Parse impedance, weight, and height measurements.

        Args:
            data: Raw bytearray
            flags: Parsed flags
            offset: Current offset
            result: Result dictionary to populate

        Returns:
            Updated offset
        """
        # Parse optional impedance
        if (flags & 0x200) and len(data) >= offset + 2:
            impedance_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["impedance"] = impedance_raw * 0.1
            result["impedance_unit"] = "ohm"
            offset += 2

        # Parse optional weight
        if (flags & 0x400) and len(data) >= offset + 2:
            weight, weight_unit = self._parse_mass_field(data, flags, offset)
            result["weight"] = weight
            result["weight_unit"] = weight_unit
            offset += 2

        # Parse optional height
        if (flags & 0x800) and len(data) >= offset + 2:
            height_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            if flags & 0x01:  # Imperial units
                height = height_raw * 0.1  # 0.1 inch resolution
                height_unit = "in"
            else:  # SI units
                height = height_raw * 0.001  # 0.001 m resolution
                height_unit = "m"
            result["height"] = height
            result["height_unit"] = height_unit
            offset += 2

        return offset

    def _parse_mass_field(
        self, data: bytearray, flags: int, offset: int
    ) -> tuple[float, str]:
        """Parse a mass field with unit conversion.

        Args:
            data: Raw bytearray
            flags: Parsed flags for unit determination
            offset: Current offset

        Returns:
            tuple: (mass_value, unit_string)
        """
        mass_raw = struct.unpack("<H", data[offset : offset + 2])[0]
        if flags & 0x01:  # Imperial units
            mass = mass_raw * 0.01  # 0.01 lb resolution
            mass_unit = "lb"
        else:  # SI units
            mass = mass_raw * 0.005  # 0.005 kg resolution
            mass_unit = "kg"
        return mass, mass_unit
