"""Cooking Step Status characteristic (0x2C28)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CookingStepStatusFlags(IntFlag):
    """Bit flags for cooking step status."""

    USER_ACTION_REQUIRED = 1 << 0
    LAST_COOKING_STEP = 1 << 1
    COOKING_STEP_STARTED = 1 << 2


class CookingStepStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cooking Step Status payload."""

    flags: CookingStepStatusFlags
    cooking_step_index: int
    remaining_time_seconds: int


class CookingStepStatusCharacteristic(BaseCharacteristic[CookingStepStatusData]):
    """Cooking Step Status characteristic (0x2C28).

    org.bluetooth.characteristic.cooking_step_status
    """

    expected_length = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookingStepStatusData:
        flags = CookingStepStatusFlags(DataParser.parse_int8(data, 0, signed=False))
        cooking_step_index = DataParser.parse_int16(data, 1, signed=False)
        remaining_time_seconds = DataParser.parse_int16(data, 3, signed=False)
        return CookingStepStatusData(
            flags=flags,
            cooking_step_index=cooking_step_index,
            remaining_time_seconds=remaining_time_seconds,
        )

    def _encode_value(self, data: CookingStepStatusData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.cooking_step_index, signed=False))
        result.extend(DataParser.encode_int16(data.remaining_time_seconds, signed=False))
        return result
