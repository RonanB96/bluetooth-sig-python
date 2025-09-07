"""Cycling Power Vector characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class CyclingPowerVectorData:
    """Parsed data from Cycling Power Vector characteristic."""
    
    flags: int
    # Will be populated by parsing logic
    crank_revolution_data: dict | None = None
    first_crank_measurement_angle: int | None = None
    instantaneous_force_magnitude_array: list[int] | None = None
    instantaneous_torque_magnitude_array: list[int] | None = None

    def __post_init__(self):
        """Validate cycling power vector data."""
        if not 0 <= self.flags <= 255:
            raise ValueError("Flags must be a uint8 value (0-255)")


@dataclass
class CyclingPowerVectorCharacteristic(BaseCharacteristic):
    """Cycling Power Vector characteristic (0x2A64).

    Used to transmit detailed cycling power vector data including force and
    torque measurements at different crank angles.
    """

    _characteristic_name: str = "Cycling Power Vector"

    def parse_value(self, data: bytearray) -> CyclingPowerVectorData:
        """Parse cycling power vector data according to Bluetooth specification.

        Format: Flags(1) + Crank Revolution Data(2) + Last Crank Event Time(2) +
        First Crank Measurement Angle(2) + [Instantaneous Force Magnitude Array] +
        [Instantaneous Torque Magnitude Array]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed cycling power vector data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 7:
            raise ValueError("Cycling Power Vector data must be at least 7 bytes")

        flags = data[0]

        # Parse crank revolution data (2 bytes)
        crank_revolutions = struct.unpack("<H", data[1:3])[0]

        # Parse last crank event time (2 bytes, 1/1024 second units)
        crank_event_time_raw = struct.unpack("<H", data[3:5])[0]
        crank_event_time = crank_event_time_raw / 1024.0

        # Parse first crank measurement angle (2 bytes, 1/180 degree units)
        first_angle_raw = struct.unpack("<H", data[5:7])[0]
        first_angle = first_angle_raw / 180.0  # Convert to degrees

        result = {
            "flags": flags,
            "crank_revolutions": crank_revolutions,
            "last_crank_event_time": crank_event_time,
            "first_crank_measurement_angle": first_angle,
        }

        offset = 7

        # Parse optional instantaneous force magnitude array if present
        if (flags & 0x01) and len(data) > offset:
            force_magnitudes: list[float] = []
            # Each force magnitude is 2 bytes (signed 16-bit, 1 N units)
            while offset + 1 < len(data) and not (
                flags & 0x02
            ):  # Stop if torque data follows
                if offset + 2 > len(data):
                    break
                force_raw = struct.unpack("<h", data[offset : offset + 2])[0]
                force_magnitudes.append(float(force_raw))  # Force in Newtons
                offset += 2

            if force_magnitudes:
                result["instantaneous_force_magnitudes"] = force_magnitudes

        # Parse optional instantaneous torque magnitude array if present
        if (flags & 0x02) and len(data) > offset:
            torque_magnitudes: list[float] = []
            # Each torque magnitude is 2 bytes (signed 16-bit, 1/32 Nm units)
            while offset + 1 < len(data):
                if offset + 2 > len(data):
                    break
                torque_raw = struct.unpack("<h", data[offset : offset + 2])[0]
                torque_magnitudes.append(torque_raw / 32.0)  # Convert to Nm
                offset += 2

            if torque_magnitudes:
                result["instantaneous_torque_magnitudes"] = torque_magnitudes

        # Convert dict to dataclass at the end (simplified conversion)
        return CyclingPowerVectorData(
            flags=result["flags"],
            crank_revolution_data=result.get("crank_revolution_data"),
            first_crank_measurement_angle=result.get("first_crank_measurement_angle"),
            instantaneous_force_magnitude_array=result.get("instantaneous_force_magnitudes"),
            instantaneous_torque_magnitude_array=result.get("instantaneous_torque_magnitudes"),
        )

    def encode_value(self, data: CyclingPowerVectorData) -> bytearray:  # pylint: disable=too-many-branches # Complex cycling power vector with optional fields
        """Encode cycling power vector value back to bytes.

        Args:
            data: CyclingPowerVectorData containing cycling power vector data

        Returns:
            Encoded bytes representing the power vector
        """
        if not isinstance(data, CyclingPowerVectorData):
            raise TypeError(
                f"Cycling power vector data must be a CyclingPowerVectorData, "
                f"got {type(data).__name__}"
            )

        # Required fields
        required_fields = [
            "crank_revolutions",
            "crank_event_time",
            "first_crank_measurement_angle",
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Power vector data must contain '{field}' key")

        crank_revolutions = int(data["crank_revolutions"])
        crank_event_time = float(data["crank_event_time"])
        first_angle = float(data["first_crank_measurement_angle"])

        # Build basic flags (simplified implementation)
        flags = 0
        if "force_magnitude_array" in data:
            flags |= 0x01  # Force magnitude array present
        if "torque_magnitude_array" in data:
            flags |= 0x02  # Torque magnitude array present

        # Convert values to raw format
        crank_event_time_raw = round(crank_event_time * 1024)  # 1/1024 second units
        first_angle_raw = round(first_angle * 180)  # 1/180 degree units

        # Validate ranges
        if not 0 <= crank_revolutions <= 0xFFFF:
            raise ValueError(
                f"Crank revolutions {crank_revolutions} exceeds uint16 range"
            )
        if not 0 <= crank_event_time_raw <= 0xFFFF:
            raise ValueError(
                f"Crank event time {crank_event_time_raw} exceeds uint16 range"
            )
        if not 0 <= first_angle_raw <= 0xFFFF:
            raise ValueError(f"First angle {first_angle_raw} exceeds uint16 range")

        # Build result
        result = bytearray([flags])
        result.extend(struct.pack("<H", crank_revolutions))
        result.extend(struct.pack("<H", crank_event_time_raw))
        result.extend(struct.pack("<H", first_angle_raw))

        # Add arrays if present (simplified implementation)
        if "force_magnitude_array" in data and isinstance(
            data["force_magnitude_array"], list
        ):
            for force in data["force_magnitude_array"]:
                force_val = int(force)
                if 0 <= force_val <= 0xFFFF:
                    result.extend(struct.pack("<H", force_val))

        if "torque_magnitude_array" in data and isinstance(
            data["torque_magnitude_array"], list
        ):
            for torque in data["torque_magnitude_array"]:
                torque_val = int(torque)
                if 0 <= torque_val <= 0xFFFF:
                    result.extend(struct.pack("<H", torque_val))

        return result
