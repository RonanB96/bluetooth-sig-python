"""Cycling Power Vector characteristic implementation."""

from __future__ import annotations

from enum import IntFlag
from typing import Any

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT8_MAX
from .base import BaseCharacteristic
from .utils import DataParser


class CyclingPowerVectorFlags(IntFlag):
    """Cycling Power Vector flags as per Bluetooth SIG specification."""

    INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT = 0x01
    INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT = 0x02


class CrankRevolutionData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Crank revolution data from cycling power vector."""

    crank_revolutions: int
    last_crank_event_time: float  # in seconds


class CyclingPowerVectorData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Cycling Power Vector characteristic.

    Used for both parsing and encoding - all fields are properly typed.
    """

    flags: int
    crank_revolution_data: CrankRevolutionData
    first_crank_measurement_angle: float
    instantaneous_force_magnitude_array: tuple[float, ...] | None = None
    instantaneous_torque_magnitude_array: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        """Validate cycling power vector data."""
        if not 0 <= self.flags <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")
        if not 0 <= self.first_crank_measurement_angle <= 360:
            raise ValueError("First crank measurement angle must be 0-360 degrees")


class CyclingPowerVectorCharacteristic(BaseCharacteristic):
    """Cycling Power Vector characteristic (0x2A64).

    Used to transmit detailed cycling power vector data including force
    and torque measurements at different crank angles.
    """

    _manual_unit: str = "various"  # Multiple units in vector data

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> CyclingPowerVectorData:
        """Parse cycling power vector data according to Bluetooth
        specification.

        Format: Flags(1) + Crank Revolution Data(2) + Last Crank Event Time(2) +
        First Crank Measurement Angle(2) + [Instantaneous Force Magnitude Array] +
        [Instantaneous Torque Magnitude Array]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            CyclingPowerVectorData containing parsed cycling power vector data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 7:
            raise ValueError("Cycling Power Vector data must be at least 7 bytes")

        flags = data[0]

        # Parse crank revolution data (2 bytes)
        crank_revolutions = DataParser.parse_int16(data, 1, signed=False)

        # Parse last crank event time (2 bytes, 1/1024 second units)
        crank_event_time_raw = DataParser.parse_int16(data, 3, signed=False)
        crank_event_time = crank_event_time_raw / 1024.0

        # Parse first crank measurement angle (2 bytes, 1/180 degree units)
        first_angle_raw = DataParser.parse_int16(data, 5, signed=False)
        first_angle = first_angle_raw / 180.0  # Convert to degrees

        # Create crank revolution data
        crank_revolution_data = CrankRevolutionData(
            crank_revolutions=crank_revolutions, last_crank_event_time=crank_event_time
        )

        offset = 7
        force_magnitudes_list: list[float] = []
        torque_magnitudes_list: list[float] = []

        # Parse optional instantaneous force magnitude array if present
        if (flags & CyclingPowerVectorFlags.INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT) and len(data) > offset:
            # Each force magnitude is 2 bytes (signed 16-bit, 1 N units)
            while offset + 1 < len(data) and not (
                flags & CyclingPowerVectorFlags.INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT
            ):  # Stop if torque data follows
                if offset + 2 > len(data):
                    break
                force_raw = DataParser.parse_int16(data, offset, signed=True)
                force_magnitudes_list.append(float(force_raw))  # Force in Newtons
                offset += 2

        # Parse optional instantaneous torque magnitude array if present
        if (flags & CyclingPowerVectorFlags.INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT) and len(data) > offset:
            # Each torque magnitude is 2 bytes (signed 16-bit, 1/32 Nm units)
            while offset + 1 < len(data):
                if offset + 2 > len(data):
                    break
                torque_raw = DataParser.parse_int16(data, offset, signed=True)
                torque_magnitudes_list.append(torque_raw / 32.0)  # Convert to Nm
                offset += 2

        return CyclingPowerVectorData(
            flags=flags,
            crank_revolution_data=crank_revolution_data,
            first_crank_measurement_angle=first_angle,
            instantaneous_force_magnitude_array=tuple(force_magnitudes_list) if force_magnitudes_list else None,
            instantaneous_torque_magnitude_array=tuple(torque_magnitudes_list) if torque_magnitudes_list else None,
        )

    def encode_value(self, data: CyclingPowerVectorData) -> bytearray:  # pylint: disable=too-many-branches # Complex cycling power vector with optional fields
        """Encode cycling power vector value back to bytes.

        Args:
            data: CyclingPowerVectorData containing cycling power vector data

        Returns:
            Encoded bytes representing the power vector
        """
        if not isinstance(data, CyclingPowerVectorData):
            raise TypeError(f"Cycling power vector data must be a CyclingPowerVectorData, got {type(data).__name__}")

        # Extract values from dataclass
        crank_revolutions = data.crank_revolution_data.crank_revolutions
        crank_event_time = data.crank_revolution_data.last_crank_event_time
        first_angle = data.first_crank_measurement_angle

        # Build flags based on optional arrays
        flags = data.flags
        if data.instantaneous_force_magnitude_array is not None:
            flags |= (
                CyclingPowerVectorFlags.INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT
            )  # Force magnitude array present
        if data.instantaneous_torque_magnitude_array is not None:
            flags |= (
                CyclingPowerVectorFlags.INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT
            )  # Torque magnitude array present

        # Convert values to raw format
        crank_event_time_raw = round(crank_event_time * 1024)  # 1/1024 second units
        first_angle_raw = round(first_angle * 180)  # 1/180 degree units

        # Validate ranges
        if not 0 <= crank_revolutions <= 0xFFFF:
            raise ValueError(f"Crank revolutions {crank_revolutions} exceeds uint16 range")
        if not 0 <= crank_event_time_raw <= 0xFFFF:
            raise ValueError(f"Crank event time {crank_event_time_raw} exceeds uint16 range")
        if not 0 <= first_angle_raw <= 0xFFFF:
            raise ValueError(f"First angle {first_angle_raw} exceeds uint16 range")

        # Build result
        result = bytearray([flags])
        result.extend(DataParser.encode_int16(crank_revolutions, signed=False))
        result.extend(DataParser.encode_int16(crank_event_time_raw, signed=False))
        result.extend(DataParser.encode_int16(first_angle_raw, signed=False))

        # Add force magnitude array if present
        if data.instantaneous_force_magnitude_array is not None:
            for force in data.instantaneous_force_magnitude_array:
                force_val = int(force)
                if SINT16_MIN <= force_val <= SINT16_MAX:  # signed 16-bit range
                    result.extend(DataParser.encode_int16(force_val, signed=True))

        # Add torque magnitude array if present
        if data.instantaneous_torque_magnitude_array is not None:
            for torque in data.instantaneous_torque_magnitude_array:
                torque_val = int(torque * 32)  # Convert back to 1/32 Nm units
                if SINT16_MIN <= torque_val <= SINT16_MAX:  # signed 16-bit range
                    result.extend(DataParser.encode_int16(torque_val, signed=True))

        return result
