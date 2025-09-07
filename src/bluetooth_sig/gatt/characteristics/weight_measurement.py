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

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode weight measurement value back to bytes.

        Args:
            data: Dictionary containing weight measurement data

        Returns:
            Encoded bytes representing the weight measurement
        """
        if not isinstance(data, dict):
            raise TypeError("Weight measurement data must be a dictionary")
        
        if "weight" not in data:
            raise ValueError("Weight measurement data must contain 'weight' key")
        
        weight = float(data["weight"])
        measurement_units = data.get("measurement_units", "metric")
        timestamp = data.get("timestamp")
        user_id = data.get("user_id")
        bmi = data.get("bmi")
        height = data.get("height")
        
        # Build flags based on available data
        flags = 0
        if measurement_units == "imperial":
            flags |= 0x01  # Imperial units flag
        if timestamp is not None:
            flags |= 0x02  # Timestamp present
        if user_id is not None:
            flags |= 0x04  # User ID present
        if bmi is not None:
            flags |= 0x08  # BMI present
        if height is not None:
            flags |= 0x10  # Height present
        
        # Convert weight to raw value based on units
        if flags & 0x01:  # Imperial units (pounds)
            weight_raw = round(weight / 0.01)  # 0.01 lb resolution
        else:  # SI units (kilograms)
            weight_raw = round(weight / 0.005)  # 0.005 kg resolution
        
        if not 0 <= weight_raw <= 0xFFFF:
            raise ValueError(f"Weight value {weight_raw} exceeds uint16 range")
        
        # Start with flags and weight
        result = bytearray([flags])
        result.extend(struct.pack("<H", weight_raw))
        
        # Add optional fields based on flags
        if timestamp is not None:
            result.extend(self._encode_ieee11073_timestamp(timestamp))
        
        if user_id is not None:
            if not 0 <= user_id <= 255:
                raise ValueError(f"User ID {user_id} exceeds uint8 range")
            result.append(user_id)
        
        if bmi is not None:
            bmi_raw = round(bmi / 0.1)  # 0.1 resolution
            if not 0 <= bmi_raw <= 0xFFFF:
                raise ValueError(f"BMI value {bmi_raw} exceeds uint16 range")
            result.extend(struct.pack("<H", bmi_raw))
        
        if height is not None:
            if flags & 0x01:  # Imperial units (inches)
                height_raw = round(height / 0.1)  # 0.1 inch resolution
            else:  # SI units (meters)
                height_raw = round(height / 0.001)  # 0.001 m resolution
            
            if not 0 <= height_raw <= 0xFFFF:
                raise ValueError(f"Height value {height_raw} exceeds uint16 range")
            result.extend(struct.pack("<H", height_raw))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "kg"  # Primary unit for weight
