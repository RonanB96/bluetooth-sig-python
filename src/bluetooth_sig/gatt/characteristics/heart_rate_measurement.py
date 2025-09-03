"""Heart Rate Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class HeartRateMeasurementCharacteristic(BaseCharacteristic):
    """Heart Rate Measurement characteristic (0x2A37).

    Used in Heart Rate Service to transmit heart rate measurements.
    """

    _characteristic_name: str = "Heart Rate Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse heart rate measurement data according to Bluetooth specification.

        Format: Flags(1) + Heart Rate Value(1-2) + [Energy Expended(2)] + [RR-Intervals(2*n)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed heart rate data with metadata
        """
        if len(data) < 2:
            raise ValueError("Heart Rate Measurement data must be at least 2 bytes")

        flags = data[0]
        offset = 1

        # Parse heart rate value
        if flags & 0x01:  # 16-bit heart rate value
            if len(data) < offset + 2:
                raise ValueError("Insufficient data for 16-bit heart rate value")
            heart_rate = struct.unpack("<H", data[offset : offset + 2])[0]
            offset += 2
        else:  # 8-bit heart rate value
            heart_rate = data[offset]
            offset += 1

        result = {
            "heart_rate": heart_rate,
            "flags": flags,
            "sensor_contact_detected": bool(flags & 0x04),
            "sensor_contact_supported": bool(flags & 0x02),
        }

        # Parse optional energy expended (2 bytes) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            energy_expended = struct.unpack("<H", data[offset : offset + 2])[0]
            result["energy_expended"] = energy_expended
            offset += 2

        # Parse optional RR-Intervals if present
        if (flags & 0x10) and len(data) >= offset + 2:
            rr_intervals = []
            while offset + 2 <= len(data):
                rr_interval = struct.unpack("<H", data[offset : offset + 2])[0]
                # RR-Interval is in 1/1024 second units
                rr_intervals.append(rr_interval / 1024.0)
                offset += 2
            result["rr_intervals"] = rr_intervals

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "bpm"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "heart_rate"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
