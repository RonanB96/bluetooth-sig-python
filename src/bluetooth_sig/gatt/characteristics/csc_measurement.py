"""CSC Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class CSCMeasurementCharacteristic(BaseCharacteristic):
    """CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B).

    Used to transmit cycling speed and cadence data.
    """

    _characteristic_name: str = "CSC Measurement"

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse CSC measurement data according to Bluetooth specification.

        Format: Flags(1) + [Cumulative Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
        [Cumulative Crank Revolutions(2)] + [Last Crank Event Time(2)]

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

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode CSC measurement value back to bytes.

        Args:
            data: Dictionary containing CSC measurement data

        Returns:
            Encoded bytes representing the CSC measurement
        """
        if not isinstance(data, dict):
            raise TypeError("CSC measurement data must be a dictionary")

        # Build flags based on available data
        flags = 0
        has_wheel_data = all(
            k in data for k in ["cumulative_wheel_revolutions", "last_wheel_event_time"]
        )
        has_crank_data = all(
            k in data for k in ["cumulative_crank_revolutions", "last_crank_event_time"]
        )

        if has_wheel_data:
            flags |= 0x01  # Wheel revolution data present
        if has_crank_data:
            flags |= 0x02  # Crank revolution data present

        # Start with flags byte
        result = bytearray([flags])

        # Add wheel revolution data if present
        if has_wheel_data:
            wheel_revolutions = int(data["cumulative_wheel_revolutions"])
            wheel_event_time = float(data["last_wheel_event_time"])

            # Validate ranges
            if not 0 <= wheel_revolutions <= 0xFFFFFFFF:
                raise ValueError(
                    f"Wheel revolutions {wheel_revolutions} exceeds uint32 range"
                )

            wheel_event_time_raw = round(
                wheel_event_time * 1024
            )  # Convert to 1/1024 second units
            if not 0 <= wheel_event_time_raw <= 0xFFFF:
                raise ValueError(
                    f"Wheel event time {wheel_event_time_raw} exceeds uint16 range"
                )

            result.extend(struct.pack("<I", wheel_revolutions))
            result.extend(struct.pack("<H", wheel_event_time_raw))

        # Add crank revolution data if present
        if has_crank_data:
            crank_revolutions = int(data["cumulative_crank_revolutions"])
            crank_event_time = float(data["last_crank_event_time"])

            # Validate ranges
            if not 0 <= crank_revolutions <= 0xFFFF:
                raise ValueError(
                    f"Crank revolutions {crank_revolutions} exceeds uint16 range"
                )

            crank_event_time_raw = round(
                crank_event_time * 1024
            )  # Convert to 1/1024 second units
            if not 0 <= crank_event_time_raw <= 0xFFFF:
                raise ValueError(
                    f"Crank event time {crank_event_time_raw} exceeds uint16 range"
                )

            result.extend(struct.pack("<H", crank_revolutions))
            result.extend(struct.pack("<H", crank_event_time_raw))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "rev"  # Revolutions
