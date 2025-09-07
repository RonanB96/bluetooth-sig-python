"""Weight Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class WeightMeasurementCharacteristic(BaseCharacteristic):
    """Weight Measurement characteristic (0x2A9D).

    Used to transmit weight measurement data with optional fields.
    Supports metric/imperial units, timestamps, user ID, BMI, and height.
    """

    _characteristic_name: str = "Weight Measurement"

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse weight measurement data according to Bluetooth specification.

        Format: Flags(1) + Weight(2) + [Timestamp(7)] + [User ID(1)] +
                [BMI(2)] + [Height(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed weight measurement data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 3:
            raise ValueError("Weight Measurement data must be at least 3 bytes")

        flags = data[0]
        offset = 1

        # Parse weight value (uint16 with 0.005 kg resolution)
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for weight value")
        weight_raw = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2

        # Convert to appropriate unit based on flags
        if flags & 0x01:  # Imperial units (pounds)
            weight = weight_raw * 0.01  # 0.01 lb resolution for imperial
            weight_unit = "lb"
        else:  # SI units (kilograms)
            weight = weight_raw * 0.005  # 0.005 kg resolution for metric
            weight_unit = "kg"

        result = {
            "weight": weight,
            "weight_unit": weight_unit,
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

        # Parse optional BMI (uint16 with 0.1 resolution) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            bmi_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["bmi"] = bmi_raw * 0.1
            offset += 2

        # Parse optional height (uint16 with 0.001m resolution) if present
        if (flags & 0x10) and len(data) >= offset + 2:
            height_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            if flags & 0x01:  # Imperial units (inches)
                result["height"] = height_raw * 0.1  # 0.1 inch resolution
                result["height_unit"] = "in"
            else:  # SI units (meters)
                result["height"] = height_raw * 0.001  # 0.001 m resolution
                result["height_unit"] = "m"
            offset += 2

        return result

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "kg"  # Primary unit for weight
