"""RSC Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class RSCMeasurementCharacteristic(BaseCharacteristic):
    """RSC (Running Speed and Cadence) Measurement characteristic (0x2A53).

    Used to transmit running speed and cadence data.
    """

    _characteristic_name: str = "RSC Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "string"  # JSON string representation
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse RSC measurement data according to Bluetooth specification.

        Format: Flags(1) + Instantaneous Speed(2) + Instantaneous Cadence(1) +
        [Instantaneous Stride Length(2)] + [Total Distance(4)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed RSC data with metadata
        """
        if len(data) < 4:
            raise ValueError("RSC Measurement data must be at least 4 bytes")

        flags = data[0]

        # Parse instantaneous speed (uint16, 1/256 m/s units)
        speed_raw = struct.unpack("<H", data[1:3])[0]
        speed_ms = speed_raw / 256.0  # m/s

        # Parse instantaneous cadence (uint8, 1/min units)
        cadence = data[3]

        result = {
            "instantaneous_speed": speed_ms,
            "instantaneous_cadence": cadence,
            "flags": flags,
        }

        offset = 4

        # Parse optional instantaneous stride length (2 bytes) if present
        if (flags & 0x01) and len(data) >= offset + 2:
            stride_length_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["instantaneous_stride_length"] = (
                stride_length_raw / 100.0
            )  # Convert to meters
            offset += 2

        # Parse optional total distance (4 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 4:
            total_distance_raw = struct.unpack("<I", data[offset : offset + 4])[0]
            result["total_distance"] = total_distance_raw / 10.0  # Convert to meters

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "m/s"  # Primary unit for speed

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "speed"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
