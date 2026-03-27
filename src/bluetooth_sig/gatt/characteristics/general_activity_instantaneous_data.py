"""General Activity Instantaneous Data characteristic (0x2B3D).

Reports instantaneous general activity data: steps, distance, duration, intensity.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GeneralActivityInstFlags(IntFlag):
    """General Activity Instantaneous Data flags."""

    STEPS_PRESENT = 0x01
    DISTANCE_PRESENT = 0x02
    DURATION_PRESENT = 0x04
    INTENSITY_PRESENT = 0x08


class GeneralActivityInstantaneousData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from General Activity Instantaneous Data characteristic.

    Attributes:
        flags: Presence flags for optional fields.
        steps: Step count. None if not present.
        distance: Distance in metres (uint24). None if not present.
        duration: Duration in seconds (uint24). None if not present.
        intensity: Activity intensity (uint8, percentage). None if not present.

    """

    flags: GeneralActivityInstFlags
    steps: int | None = None
    distance: int | None = None
    duration: int | None = None
    intensity: int | None = None


class GeneralActivityInstantaneousDataCharacteristic(BaseCharacteristic[GeneralActivityInstantaneousData]):
    """General Activity Instantaneous Data characteristic (0x2B3D).

    org.bluetooth.characteristic.general_activity_instantaneous_data

    Reports instantaneous general activity data.
    """

    min_length = 1  # flags only
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GeneralActivityInstantaneousData:
        """Parse General Activity Instantaneous Data.

        Format: Flags (uint8) + [Steps (uint16)] + [Distance (uint24)]
                + [Duration (uint24)] + [Intensity (uint8)].
        """
        flags = GeneralActivityInstFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        steps: int | None = None
        if flags & GeneralActivityInstFlags.STEPS_PRESENT and len(data) >= offset + 2:
            steps = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        distance: int | None = None
        if flags & GeneralActivityInstFlags.DISTANCE_PRESENT and len(data) >= offset + 3:
            distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        duration: int | None = None
        if flags & GeneralActivityInstFlags.DURATION_PRESENT and len(data) >= offset + 3:
            duration = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        intensity: int | None = None
        if flags & GeneralActivityInstFlags.INTENSITY_PRESENT and len(data) >= offset + 1:
            intensity = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        return GeneralActivityInstantaneousData(
            flags=flags,
            steps=steps,
            distance=distance,
            duration=duration,
            intensity=intensity,
        )

    def _encode_value(self, data: GeneralActivityInstantaneousData) -> bytearray:
        """Encode General Activity Instantaneous data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))

        if data.steps is not None:
            result.extend(DataParser.encode_int16(data.steps, signed=False))
        if data.distance is not None:
            result.extend(DataParser.encode_int24(data.distance, signed=False))
        if data.duration is not None:
            result.extend(DataParser.encode_int24(data.duration, signed=False))
        if data.intensity is not None:
            result.extend(DataParser.encode_int8(data.intensity, signed=False))

        return result
