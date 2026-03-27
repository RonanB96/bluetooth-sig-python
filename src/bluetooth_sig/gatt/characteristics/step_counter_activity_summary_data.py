"""Step Counter Activity Summary Data characteristic (0x2B40).

Flags-based summary of step counter activity data.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class StepCounterActivitySummaryFlags(IntFlag):
    """Step Counter Activity Summary Data flags."""

    STEP_COUNT_PRESENT = 0x0001
    DISTANCE_PRESENT = 0x0002
    CALORIES_PRESENT = 0x0004


class StepCounterActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Step Counter Activity Summary Data.

    Attributes:
        flags: Presence flags for optional fields.
        step_count: Step count (uint24). None if not present.
        distance: Distance in metres (uint24). None if not present.
        calories: Calories burned (uint16). None if not present.

    """

    flags: StepCounterActivitySummaryFlags
    step_count: int | None = None
    distance: int | None = None
    calories: int | None = None


class StepCounterActivitySummaryDataCharacteristic(
    BaseCharacteristic[StepCounterActivitySummaryData],
):
    """Step Counter Activity Summary Data characteristic (0x2B40).

    org.bluetooth.characteristic.step_counter_activity_summary_data

    Summary of step counter activity with optional fields indicated
    by a flags field.
    """

    min_length = 2  # flags only (uint16)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> StepCounterActivitySummaryData:
        """Parse Step Counter Activity Summary Data.

        Format: Flags (uint16) + [Step Count (uint24)] + [Distance (uint24)]
                + [Calories (uint16)].
        """
        flags = StepCounterActivitySummaryFlags(DataParser.parse_int16(data, 0, signed=False))
        offset = 2

        step_count: int | None = None
        if flags & StepCounterActivitySummaryFlags.STEP_COUNT_PRESENT and len(data) >= offset + 3:
            step_count = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        distance: int | None = None
        if flags & StepCounterActivitySummaryFlags.DISTANCE_PRESENT and len(data) >= offset + 3:
            distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        calories: int | None = None
        if flags & StepCounterActivitySummaryFlags.CALORIES_PRESENT and len(data) >= offset + 2:
            calories = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        return StepCounterActivitySummaryData(
            flags=flags,
            step_count=step_count,
            distance=distance,
            calories=calories,
        )

    def _encode_value(self, data: StepCounterActivitySummaryData) -> bytearray:
        """Encode Step Counter Activity Summary Data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))

        if data.step_count is not None:
            result.extend(DataParser.encode_int24(data.step_count, signed=False))
        if data.distance is not None:
            result.extend(DataParser.encode_int24(data.distance, signed=False))
        if data.calories is not None:
            result.extend(DataParser.encode_int16(data.calories, signed=False))

        return result
