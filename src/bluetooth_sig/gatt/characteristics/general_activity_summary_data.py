"""General Activity Summary Data characteristic (0x2B3E).

Reports summary statistics for a general activity period.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GeneralActivitySummaryFlags(IntFlag):
    """General Activity Summary Data flags."""

    STEPS_PRESENT = 0x01
    DISTANCE_PRESENT = 0x02
    DURATION_PRESENT = 0x04
    INTENSITY_PRESENT = 0x08
    CALORIES_PRESENT = 0x10


class GeneralActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from General Activity Summary Data characteristic.

    Attributes:
        flags: Presence flags for optional fields.
        steps: Total step count for the period. None if not present.
        distance: Total distance in metres (uint24). None if not present.
        duration: Total duration in seconds (uint24). None if not present.
        intensity: Average intensity (uint8, percentage). None if not present.
        calories: Energy expenditure in kilocalories (uint16). None if not present.

    """

    flags: GeneralActivitySummaryFlags
    steps: int | None = None
    distance: int | None = None
    duration: int | None = None
    intensity: int | None = None
    calories: int | None = None


class GeneralActivitySummaryDataCharacteristic(BaseCharacteristic[GeneralActivitySummaryData]):
    """General Activity Summary Data characteristic (0x2B3E).

    org.bluetooth.characteristic.general_activity_summary_data

    Reports summary statistics for a general activity period.
    """

    min_length = 1  # flags only
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GeneralActivitySummaryData:
        """Parse General Activity Summary Data.

        Format: Flags (uint8) + [Steps (uint16)] + [Distance (uint24)]
                + [Duration (uint24)] + [Intensity (uint8)] + [Calories (uint16)].
        """
        flags = GeneralActivitySummaryFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        steps: int | None = None
        if flags & GeneralActivitySummaryFlags.STEPS_PRESENT and len(data) >= offset + 2:
            steps = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        distance: int | None = None
        if flags & GeneralActivitySummaryFlags.DISTANCE_PRESENT and len(data) >= offset + 3:
            distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        duration: int | None = None
        if flags & GeneralActivitySummaryFlags.DURATION_PRESENT and len(data) >= offset + 3:
            duration = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        intensity: int | None = None
        if flags & GeneralActivitySummaryFlags.INTENSITY_PRESENT and len(data) >= offset + 1:
            intensity = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        calories: int | None = None
        if flags & GeneralActivitySummaryFlags.CALORIES_PRESENT and len(data) >= offset + 2:
            calories = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        return GeneralActivitySummaryData(
            flags=flags,
            steps=steps,
            distance=distance,
            duration=duration,
            intensity=intensity,
            calories=calories,
        )

    def _encode_value(self, data: GeneralActivitySummaryData) -> bytearray:
        """Encode General Activity Summary data."""
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
        if data.calories is not None:
            result.extend(DataParser.encode_int16(data.calories, signed=False))

        return result
