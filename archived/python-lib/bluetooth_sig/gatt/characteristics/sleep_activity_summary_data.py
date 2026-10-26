"""Sleep Activity Summary Data characteristic (0x2B42)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SleepActivitySummaryFlags(IntFlag):
    """Flags for Sleep Activity Summary Data (Table 3.20)."""

    TOTAL_SLEEP_TIME_PRESENT = 0x000001
    TOTAL_WAKE_TIME_PRESENT = 0x000002
    TOTAL_BED_TIME_PRESENT = 0x000004
    NUMBER_OF_AWAKENINGS_PRESENT = 0x000008
    SLEEP_LATENCY_PRESENT = 0x000010
    SLEEP_EFFICIENCY_PRESENT = 0x000020
    SNOOZE_TIME_PRESENT = 0x000040
    TOSS_TURN_EVENTS_PRESENT = 0x000080
    AWAKENING_AFTER_ALARM_PRESENT = 0x000100
    MIN_VISIBLE_LIGHT_PRESENT = 0x000200
    MAX_VISIBLE_LIGHT_PRESENT = 0x000400
    AVG_VISIBLE_LIGHT_PRESENT = 0x000800
    MIN_UV_LIGHT_PRESENT = 0x001000
    MAX_UV_LIGHT_PRESENT = 0x002000
    AVG_UV_LIGHT_PRESENT = 0x004000
    MIN_IR_LIGHT_PRESENT = 0x008000
    MAX_IR_LIGHT_PRESENT = 0x010000
    AVG_IR_LIGHT_PRESENT = 0x020000
    AVG_SLEEPING_HR_PRESENT = 0x040000
    WORN_DURATION_PRESENT = 0x080000


_ADDITIONAL_DATA_START_OFFSET = 3


class SleepActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Sleep Activity Summary Data.

    Contains flags and any additional summary field data as raw bytes.
    The flags field indicates which optional summary fields are present.
    """

    flags: SleepActivitySummaryFlags
    additional_data: bytes = b""


class SleepActivitySummaryDataCharacteristic(
    BaseCharacteristic[SleepActivitySummaryData],
):
    """Sleep Activity Summary Data characteristic (0x2B42).

    org.bluetooth.characteristic.sleep_activity_summary_data

    Summary sleep activity data from the Physical Activity Monitor
    service. Flags indicate which optional summary fields are present.
    """

    min_length = 3  # flags (uint24)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SleepActivitySummaryData:
        """Parse Sleep Activity Summary Data.

        Format: flags (uint24) + variable optional fields.
        """
        flags = SleepActivitySummaryFlags(DataParser.parse_int24(data, 0, signed=False))
        additional_data = (
            bytes(data[_ADDITIONAL_DATA_START_OFFSET:]) if len(data) > _ADDITIONAL_DATA_START_OFFSET else b""
        )

        return SleepActivitySummaryData(
            flags=flags,
            additional_data=additional_data,
        )

    def _encode_value(self, data: SleepActivitySummaryData) -> bytearray:
        """Encode Sleep Activity Summary Data to bytes."""
        result = bytearray()
        result += DataParser.encode_int24(int(data.flags), signed=False)
        result += bytearray(data.additional_data)
        return result
