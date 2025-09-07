"""Temperature Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class TemperatureMeasurementCharacteristic(BaseCharacteristic):
    """Temperature Measurement characteristic (0x2A1C).

    Used in Health Thermometer Service for medical temperature readings.
    Different from Environmental Temperature (0x2A6E).
    """

    _characteristic_name: str = "Temperature Measurement"

    def parse_value(self, data: bytearray) -> dict[str, Any]:  # pylint: disable=too-many-locals
        """Parse temperature measurement data according to Bluetooth specification.

        Format: Flags(1) + Temperature Value(4) + [Timestamp(7)] + [Temperature Type(1)]
        Temperature is IEEE-11073 32-bit float.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed temperature data with metadata
        """
        if len(data) < 5:
            raise ValueError("Temperature Measurement data must be at least 5 bytes")

        flags = data[0]

        # Parse temperature value (IEEE-11073 32-bit float)
        temp_bytes = data[1:5]
        temp_value = struct.unpack("<f", temp_bytes)[0]

        # Check temperature unit flag (bit 0)
        unit = "°F" if (flags & 0x01) else "°C"

        result = {"temperature": temp_value, "unit": unit, "flags": flags}

        # Parse optional timestamp (7 bytes) if present
        offset = 5
        if (flags & 0x02) and len(data) >= offset + 7:
            result["timestamp"] = self._parse_ieee11073_timestamp(data, offset)
            offset += 7

        # Parse optional temperature type (1 byte) if present
        if (flags & 0x04) and len(data) >= offset + 1:
            temp_type = data[offset]
            result["temperature_type"] = temp_type

        return result

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode temperature measurement value back to bytes.

        Args:
            data: Dictionary containing temperature measurement data

        Returns:
            Encoded bytes representing the temperature measurement
        """
        if not isinstance(data, dict):
            raise TypeError("Temperature measurement data must be a dictionary")

        if "temperature" not in data:
            raise ValueError(
                "Temperature measurement data must contain 'temperature' key"
            )

        temperature = float(data["temperature"])
        unit = data.get("unit", "°C")
        timestamp = data.get("timestamp")
        temp_type = data.get("temperature_type")

        # Build flags
        flags = 0
        if unit == "°F":
            flags |= 0x01  # Temperature unit flag (Fahrenheit)
        if timestamp is not None:
            flags |= 0x02  # Timestamp present
        if temp_type is not None:
            flags |= 0x04  # Temperature type present

        # Start with flags byte
        result = bytearray([flags])

        # Add temperature value (IEEE-11073 32-bit float)
        temp_bytes = struct.pack("<f", temperature)
        result.extend(temp_bytes)

        # Add optional timestamp (7 bytes) if present
        if timestamp is not None:
            result.extend(self._encode_ieee11073_timestamp(timestamp))

        # Add optional temperature type (1 byte) if present
        if temp_type is not None:
            result.append(int(temp_type))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C/°F"  # Unit depends on flags
