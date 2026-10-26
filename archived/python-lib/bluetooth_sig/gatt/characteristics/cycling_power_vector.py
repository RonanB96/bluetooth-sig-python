"""Cycling Power Vector characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CyclingPowerVectorFlags(IntFlag):
    """Cycling Power Vector flags as per CPS v1.1 Table 3.7."""

    CRANK_REVOLUTION_DATA_PRESENT = 0x01
    FIRST_CRANK_MEASUREMENT_ANGLE_PRESENT = 0x02
    INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT = 0x04
    INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT = 0x08
    INSTANTANEOUS_MEASUREMENT_DIRECTION_BIT0 = 0x10
    INSTANTANEOUS_MEASUREMENT_DIRECTION_BIT1 = 0x20


class CrankRevolutionData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Crank revolution data from cycling power vector."""

    crank_revolutions: int
    last_crank_event_time: float  # in seconds


class CyclingPowerVectorData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Cycling Power Vector characteristic.

    Used for both parsing and encoding - all fields are properly typed.
    """

    flags: CyclingPowerVectorFlags
    crank_revolution_data: CrankRevolutionData | None = None
    first_crank_measurement_angle: float | None = None
    instantaneous_force_magnitude_array: tuple[float, ...] | None = None
    instantaneous_torque_magnitude_array: tuple[float, ...] | None = None
    instantaneous_measurement_direction: int = 0


class CyclingPowerVectorCharacteristic(BaseCharacteristic[CyclingPowerVectorData]):
    """Cycling Power Vector characteristic (0x2A64).

    Used to transmit detailed cycling power vector data including force
    and torque measurements at different crank angles.
    """

    # Variable length: min 1 byte (flags only), optional crank data + angle + arrays
    min_length = 1
    allow_variable_length = True

    _manual_unit: str = "various"  # Multiple units in vector data

    _DIRECTION_MASK = 0x30
    _DIRECTION_SHIFT = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CyclingPowerVectorData:  # pylint: disable=too-many-locals  # Vector data with multiple array fields
        """Parse cycling power vector data according to CPS v1.1.

        Format: Flags(1) + [Crank Revolutions(2) + Last Crank Event Time(2)] +
        [First Crank Measurement Angle(2)] + [Force Magnitude Array(sint16[])] +
        [Torque Magnitude Array(sint16[])]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            CyclingPowerVectorData containing parsed cycling power vector data.

        """
        flags = CyclingPowerVectorFlags(data[0])
        offset = 1

        crank_revolution_data: CrankRevolutionData | None = None
        first_crank_measurement_angle: float | None = None

        # Parse crank revolution data if present (bit 0)
        if (flags & CyclingPowerVectorFlags.CRANK_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 4:
            crank_revolutions = DataParser.parse_int16(data, offset, signed=False)
            crank_event_time_raw = DataParser.parse_int16(data, offset + 2, signed=False)
            crank_revolution_data = CrankRevolutionData(
                crank_revolutions=crank_revolutions,
                last_crank_event_time=crank_event_time_raw / 1024.0,
            )
            offset += 4

        # Parse first crank measurement angle if present (bit 1)
        if (flags & CyclingPowerVectorFlags.FIRST_CRANK_MEASUREMENT_ANGLE_PRESENT) and len(data) >= offset + 2:
            first_crank_measurement_angle = DataParser.parse_int16(data, offset, signed=False) / 1.0
            offset += 2

        # Extract instantaneous measurement direction (bits 4-5)
        direction = (int(flags) & self._DIRECTION_MASK) >> self._DIRECTION_SHIFT

        force_magnitudes_list: list[float] = []
        torque_magnitudes_list: list[float] = []

        # Parse force magnitude array if present (bit 2)
        if flags & CyclingPowerVectorFlags.INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT:
            while offset + 2 <= len(data):
                force_raw = DataParser.parse_int16(data, offset, signed=True)
                force_magnitudes_list.append(float(force_raw))
                offset += 2

        # Parse torque magnitude array if present (bit 3)
        if flags & CyclingPowerVectorFlags.INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT:
            while offset + 2 <= len(data):
                torque_raw = DataParser.parse_int16(data, offset, signed=True)
                torque_magnitudes_list.append(torque_raw / 32.0)
                offset += 2

        return CyclingPowerVectorData(
            flags=flags,
            crank_revolution_data=crank_revolution_data,
            first_crank_measurement_angle=first_crank_measurement_angle,
            instantaneous_force_magnitude_array=tuple(force_magnitudes_list) if force_magnitudes_list else None,
            instantaneous_torque_magnitude_array=tuple(torque_magnitudes_list) if torque_magnitudes_list else None,
            instantaneous_measurement_direction=direction,
        )

    def _encode_value(self, data: CyclingPowerVectorData) -> bytearray:  # pylint: disable=too-many-branches # Complex cycling power vector with optional fields
        """Encode cycling power vector value back to bytes.

        Args:
            data: CyclingPowerVectorData containing cycling power vector data

        Returns:
            Encoded bytes representing the power vector

        """
        flags = int(data.flags)

        result = bytearray([flags])

        # Encode crank revolution data if present
        if data.crank_revolution_data is not None:
            crank_revolutions = data.crank_revolution_data.crank_revolutions
            crank_event_time_raw = round(data.crank_revolution_data.last_crank_event_time * 1024)
            result.extend(DataParser.encode_int16(crank_revolutions, signed=False))
            result.extend(DataParser.encode_int16(crank_event_time_raw, signed=False))

        # Encode first crank measurement angle if present
        if data.first_crank_measurement_angle is not None:
            result.extend(DataParser.encode_int16(round(data.first_crank_measurement_angle), signed=False))

        # Encode force magnitude array if present
        if data.instantaneous_force_magnitude_array is not None:
            for force in data.instantaneous_force_magnitude_array:
                force_val = int(force)
                if SINT16_MIN <= force_val <= SINT16_MAX:
                    result.extend(DataParser.encode_int16(force_val, signed=True))

        # Encode torque magnitude array if present
        if data.instantaneous_torque_magnitude_array is not None:
            for torque in data.instantaneous_torque_magnitude_array:
                torque_val = int(torque * 32)
                if SINT16_MIN <= torque_val <= SINT16_MAX:
                    result.extend(DataParser.encode_int16(torque_val, signed=True))

        return result
