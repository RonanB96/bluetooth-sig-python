"""RSC Measurement characteristic implementation."""

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class RSCMeasurementData:
    """Parsed data from RSC Measurement characteristic."""

    instantaneous_speed: float  # m/s
    instantaneous_cadence: int  # steps per minute
    flags: int
    instantaneous_stride_length: float | None = None  # meters
    total_distance: float | None = None  # meters

    def __post_init__(self):
        """Validate RSC measurement data."""
        if not 0 <= self.flags <= 255:
            raise ValueError("Flags must be a uint8 value (0-255)")
        if not 0 <= self.instantaneous_cadence <= 255:
            raise ValueError("Cadence must be a uint8 value (0-255)")


@dataclass
class RSCMeasurementCharacteristic(BaseCharacteristic):
    """RSC (Running Speed and Cadence) Measurement characteristic (0x2A53).

    Used to transmit running speed and cadence data.
    """

    _characteristic_name: str = "RSC Measurement"

    def parse_value(self, data: bytearray) -> RSCMeasurementData:
        """Parse RSC measurement data according to Bluetooth specification.

        Format: Flags(1) + Instantaneous Speed(2) + Instantaneous Cadence(1) +
        [Instantaneous Stride Length(2)] + [Total Distance(4)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            RSCMeasurementData containing parsed RSC data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("RSC Measurement data must be at least 4 bytes")

        flags = data[0]

        # Parse instantaneous speed (uint16, 1/256 m/s units)
        speed_raw = struct.unpack("<H", data[1:3])[0]
        speed_ms = speed_raw / 256.0  # m/s

        # Parse instantaneous cadence (uint8, 1/min units)
        cadence = data[3]

        # Initialize optional fields
        instantaneous_stride_length = None
        total_distance = None

        offset = 4

        # Parse optional instantaneous stride length (2 bytes) if present
        if (flags & 0x01) and len(data) >= offset + 2:
            stride_length_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            instantaneous_stride_length = stride_length_raw / 100.0  # Convert to meters
            offset += 2

        # Parse optional total distance (4 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 4:
            total_distance_raw = struct.unpack("<I", data[offset : offset + 4])[0]
            total_distance = total_distance_raw / 10.0  # Convert to meters

        return RSCMeasurementData(
            instantaneous_speed=speed_ms,
            instantaneous_cadence=cadence,
            flags=flags,
            instantaneous_stride_length=instantaneous_stride_length,
            total_distance=total_distance,
        )

    def encode_value(self, data: RSCMeasurementData) -> bytearray:
        """Encode RSC measurement value back to bytes.

        Args:
            data: RSCMeasurementData containing RSC measurement data

        Returns:
            Encoded bytes representing the RSC measurement
        """
        if not isinstance(data, RSCMeasurementData):
            raise TypeError(
                f"RSC measurement data must be a RSCMeasurementData, "
                f"got {type(data).__name__}"
            )

        # Build flags based on available optional data
        flags = data.flags
        has_stride_length = data.instantaneous_stride_length is not None
        has_total_distance = data.total_distance is not None

        # Update flags to match available data
        if has_stride_length:
            flags |= 0x01  # Instantaneous stride length present
        if has_total_distance:
            flags |= 0x02  # Total distance present

        # Validate required fields
        speed_raw = round(data.instantaneous_speed * 256)  # Convert to 1/256 m/s units
        if not 0 <= speed_raw <= 0xFFFF:
            raise ValueError(
                f"Speed {data.instantaneous_speed} m/s exceeds uint16 range"
            )

        if not 0 <= data.instantaneous_cadence <= 255:
            raise ValueError(
                f"Cadence {data.instantaneous_cadence} exceeds uint8 range"
            )

        # Start with flags, speed, and cadence
        result = bytearray([flags])
        result.extend(struct.pack("<H", speed_raw))
        result.append(data.instantaneous_cadence)

        # Add optional stride length if present
        if has_stride_length:
            stride_length = float(data.instantaneous_stride_length)
            stride_length_raw = round(stride_length * 100)  # Convert to cm units
            if not 0 <= stride_length_raw <= 0xFFFF:
                raise ValueError(
                    f"Stride length {stride_length} m exceeds uint16 range"
                )
            result.extend(struct.pack("<H", stride_length_raw))

        # Add optional total distance if present
        if has_total_distance:
            total_distance = float(data.total_distance)
            total_distance_raw = round(total_distance * 10)  # Convert to dm units
            if not 0 <= total_distance_raw <= 0xFFFFFFFF:
                raise ValueError(
                    f"Total distance {total_distance} m exceeds uint32 range"
                )
            result.extend(struct.pack("<I", total_distance_raw))

        return result
