"""Blood Pressure Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class BloodPressureMeasurementCharacteristic(BaseCharacteristic):
    """Blood Pressure Measurement characteristic (0x2A35).

    Used to transmit blood pressure measurements with systolic, diastolic and mean arterial pressure.
    """

    _characteristic_name: str = "Blood Pressure Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(
        self, data: bytearray
    ) -> dict[str, Any]:  # pylint: disable=too-many-locals
        """Parse blood pressure measurement data according to Bluetooth specification.

        Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] +
        [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)]
        All pressure values are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed blood pressure data with metadata
        """
        if len(data) < 7:
            raise ValueError("Blood Pressure Measurement data must be at least 7 bytes")

        flags = data[0]

        # Parse pressure values using IEEE-11073 SFLOAT format
        systolic_raw, diastolic_raw, map_raw = struct.unpack("<HHH", data[1:7])

        result = {
            "systolic": self._parse_ieee11073_sfloat(systolic_raw),
            "diastolic": self._parse_ieee11073_sfloat(diastolic_raw),
            "mean_arterial_pressure": self._parse_ieee11073_sfloat(map_raw),
            "unit": "kPa" if flags & 0x01 else "mmHg",  # Units flag
        }

        offset = 7

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 7:
            result["timestamp"] = self._parse_ieee11073_timestamp(data, offset)
            offset += 7

        # Parse optional pulse rate (2 bytes) if present
        if (flags & 0x04) and len(data) >= offset + 2:
            pulse_rate_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["pulse_rate"] = self._parse_ieee11073_sfloat(pulse_rate_raw)
            offset += 2

        # Parse optional user ID (1 byte) if present
        if (flags & 0x08) and len(data) >= offset + 1:
            result["user_id"] = data[offset]
            offset += 1

        # Parse optional measurement status (2 bytes) if present
        if (flags & 0x10) and len(data) >= offset + 2:
            result["measurement_status"] = struct.unpack(
                "<H", data[offset : offset + 2]
            )[0]

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mmHg/kPa"  # Unit depends on flags
