"""CSC Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class CSCMeasurementCharacteristic(BaseCharacteristic):
    """CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B).

    Used to transmit cycling speed and cadence data.
    """

    _characteristic_name: str = "CSC Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "string"  # JSON string representation
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse CSC measurement data according to Bluetooth specification.

        Format: Flags(1) + [Cumulative Wheel Revolutions(4)] + [Last Wheel Event Time(2)] + [Cumulative Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed CSC data with metadata
        """
        if len(data) < 1:
            raise ValueError("CSC Measurement data must be at least 1 byte")

        flags = data[0]
        offset = 1

        result = {"flags": flags}

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & 0x01) and len(data) >= offset + 6:
            wheel_revolutions = struct.unpack("<I", data[offset : offset + 4])[0]
            wheel_event_time_raw = struct.unpack("<H", data[offset + 4 : offset + 6])[0]
            # Wheel event time is in 1/1024 second units
            wheel_event_time = wheel_event_time_raw / 1024.0

            result.update(
                {
                    "cumulative_wheel_revolutions": wheel_revolutions,
                    "last_wheel_event_time": wheel_event_time,
                }
            )
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & 0x02) and len(data) >= offset + 4:
            crank_revolutions = struct.unpack("<H", data[offset : offset + 2])[0]
            crank_event_time_raw = struct.unpack("<H", data[offset + 2 : offset + 4])[0]
            # Crank event time is in 1/1024 second units
            crank_event_time = crank_event_time_raw / 1024.0

            result.update(
                {
                    "cumulative_crank_revolutions": crank_revolutions,
                    "last_crank_event_time": crank_event_time,
                }
            )

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "rev"  # Revolutions

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "speed"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "total_increasing"
