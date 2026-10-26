"""Sleep Activity Instantaneous Data characteristic (0x2B41)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SleepActivityInstantaneousFlags(IntFlag):
    """Flags for Sleep Activity Instantaneous Data (Table 3.17)."""

    VISIBLE_LIGHT_LEVEL_PRESENT = 0x0001
    UV_LIGHT_LEVEL_PRESENT = 0x0002
    IR_LIGHT_LEVEL_PRESENT = 0x0004
    SLEEP_STAGE_PRESENT = 0x0008
    SLEEPING_HEART_RATE_PRESENT = 0x0010
    DEVICE_WORN = 0x8000


class SleepStage(IntFlag):
    """Sleep stage bitfield (Table 3.18)."""

    WAKE = 0x000001
    SLEEP = 0x000002
    REM = 0x000004
    NON_REM = 0x000008
    LIGHT_SLEEP = 0x000010
    DEEP_SLEEP = 0x000020
    N1 = 0x000040
    N2 = 0x000080
    N3 = 0x000100
    N4 = 0x000200
    ACTIVE_SLEEP = 0x000400
    QUIET_SLEEP = 0x000800
    INTERMEDIATE_SLEEP = 0x001000
    AROUSAL = 0x002000
    UNKNOWN = 0x800000


_ADDITIONAL_DATA_START_OFFSET = 5


class SleepActivityInstantaneousData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Sleep Activity Instantaneous Data.

    Contains flags, sleep state, and any additional optional
    field data as raw bytes.
    """

    flags: SleepActivityInstantaneousFlags
    sleep_stage: SleepStage
    additional_data: bytes = b""


class SleepActivityInstantaneousDataCharacteristic(
    BaseCharacteristic[SleepActivityInstantaneousData],
):
    """Sleep Activity Instantaneous Data characteristic (0x2B41).

    org.bluetooth.characteristic.sleep_activity_instantaneous_data

    Instantaneous sleep activity data from the Physical Activity
    Monitor service. Contains the current sleep state and optional
    additional fields indicated by flags.
    """

    min_length = 5  # flags (uint16) + sleep_stage (uint24)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SleepActivityInstantaneousData:
        """Parse Sleep Activity Instantaneous Data.

        Format: flags (uint16) + sleep_stage (uint24) + optional fields.
        """
        flags = SleepActivityInstantaneousFlags(DataParser.parse_int16(data, 0, signed=False))
        sleep_stage = SleepStage(DataParser.parse_int24(data, 2, signed=False))
        additional_data = (
            bytes(data[_ADDITIONAL_DATA_START_OFFSET:]) if len(data) > _ADDITIONAL_DATA_START_OFFSET else b""
        )

        return SleepActivityInstantaneousData(
            flags=flags,
            sleep_stage=sleep_stage,
            additional_data=additional_data,
        )

    def _encode_value(self, data: SleepActivityInstantaneousData) -> bytearray:
        """Encode Sleep Activity Instantaneous Data to bytes."""
        result = bytearray()
        result += DataParser.encode_int16(int(data.flags), signed=False)
        result += DataParser.encode_int24(int(data.sleep_stage), signed=False)
        result += bytearray(data.additional_data)
        return result
