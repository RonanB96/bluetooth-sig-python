"""Body Composition Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class BodyCompositionMeasurementCharacteristic(BaseCharacteristic):
    """Body Composition Measurement characteristic (0x2A9C).

    Used to transmit body composition measurement data including body fat percentage,
    muscle mass, bone mass, water percentage, and other body metrics.
    """

    _characteristic_name: str = "Body Composition Measurement"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"  # JSON string representation of measurement data
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
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

        # Parse flags (2 bytes)
        flags = struct.unpack("<H", data[:2])[0]
        offset = 2

        # Parse body fat percentage (uint16 with 0.1% resolution)
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for body fat percentage")
        body_fat_raw = struct.unpack("<H", data[offset:offset + 2])[0]
        offset += 2

        # Convert to percentage (0.1% resolution)
        body_fat_percentage = body_fat_raw * 0.1

        result = {
            "body_fat_percentage": body_fat_percentage,
            "flags": flags,
            "measurement_units": "imperial" if (flags & 0x01) else "metric",
        }

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 7:
            timestamp = self._parse_ieee11073_timestamp(data, offset)
            result["timestamp"] = timestamp
            offset += 7

        # Parse optional user ID (1 byte) if present
        if (flags & 0x04) and len(data) >= offset + 1:
            user_id = data[offset]
            result["user_id"] = user_id
            offset += 1

        # Parse optional basal metabolism (uint16) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            basal_metabolism_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            result["basal_metabolism"] = basal_metabolism_raw  # in kJ
            result["basal_metabolism_unit"] = "kJ"
            offset += 2

        # Parse optional muscle mass (uint16 with same resolution as weight) if present
        if (flags & 0x10) and len(data) >= offset + 2:
            muscle_mass_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                muscle_mass = muscle_mass_raw * 0.01  # 0.01 lb resolution
                mass_unit = "lb"
            else:  # SI units
                muscle_mass = muscle_mass_raw * 0.005  # 0.005 kg resolution
                mass_unit = "kg"
            result["muscle_mass"] = muscle_mass
            result["muscle_mass_unit"] = mass_unit
            offset += 2

        # Parse optional muscle percentage (uint16 with 0.1% resolution) if present
        if (flags & 0x20) and len(data) >= offset + 2:
            muscle_percentage_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            result["muscle_percentage"] = muscle_percentage_raw * 0.1
            offset += 2

        # Parse optional fat free mass (uint16 with same resolution as weight)
        # if present
        if (flags & 0x40) and len(data) >= offset + 2:
            fat_free_mass_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                fat_free_mass = fat_free_mass_raw * 0.01  # 0.01 lb resolution
                mass_unit = "lb"
            else:  # SI units
                fat_free_mass = fat_free_mass_raw * 0.005  # 0.005 kg resolution
                mass_unit = "kg"
            result["fat_free_mass"] = fat_free_mass
            result["fat_free_mass_unit"] = mass_unit
            offset += 2

        # Parse optional soft lean mass (uint16 with same resolution as weight)
        # if present
        if (flags & 0x80) and len(data) >= offset + 2:
            soft_lean_mass_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                soft_lean_mass = soft_lean_mass_raw * 0.01  # 0.01 lb resolution
                mass_unit = "lb"
            else:  # SI units
                soft_lean_mass = soft_lean_mass_raw * 0.005  # 0.005 kg resolution
                mass_unit = "kg"
            result["soft_lean_mass"] = soft_lean_mass
            result["soft_lean_mass_unit"] = mass_unit
            offset += 2

        # Parse optional body water mass (uint16 with same resolution as weight)
        # if present
        if (flags & 0x100) and len(data) >= offset + 2:
            body_water_mass_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                body_water_mass = body_water_mass_raw * 0.01  # 0.01 lb resolution
                mass_unit = "lb"
            else:  # SI units
                body_water_mass = body_water_mass_raw * 0.005  # 0.005 kg resolution
                mass_unit = "kg"
            result["body_water_mass"] = body_water_mass
            result["body_water_mass_unit"] = mass_unit
            offset += 2

        # Parse optional impedance (uint16 with 0.1 ohm resolution) if present
        if (flags & 0x200) and len(data) >= offset + 2:
            impedance_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            result["impedance"] = impedance_raw * 0.1
            result["impedance_unit"] = "ohm"
            offset += 2

        # Parse optional weight (uint16 with same resolution as weight scale) if present
        if (flags & 0x400) and len(data) >= offset + 2:
            weight_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                weight = weight_raw * 0.01  # 0.01 lb resolution
                weight_unit = "lb"
            else:  # SI units
                weight = weight_raw * 0.005  # 0.005 kg resolution
                weight_unit = "kg"
            result["weight"] = weight
            result["weight_unit"] = weight_unit
            offset += 2

        # Parse optional height (uint16 with height resolution) if present
        if (flags & 0x800) and len(data) >= offset + 2:
            height_raw = struct.unpack("<H", data[offset:offset + 2])[0]
            if flags & 0x01:  # Imperial units
                height = height_raw * 0.1  # 0.1 inch resolution
                height_unit = "in"
            else:  # SI units
                height = height_raw * 0.001  # 0.001 m resolution
                height_unit = "m"
            result["height"] = height
            result["height_unit"] = height_unit
            offset += 2

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "%"  # Primary unit for body fat percentage

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "body_fat"  # Custom device class for body composition

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"