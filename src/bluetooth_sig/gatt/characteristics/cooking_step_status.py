"""Cooking Step Status characteristic (0x2C28)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.types import SpecialValueResult, SpecialValueType

from ..context import CharacteristicContext
from ..exceptions import SpecialValueDetectedError
from .base import BaseCharacteristic
from .cooking_common import validate_flags
from .utils import DataParser

_REMAINING_TIME_MAX_SECONDS = 0xFF00
_REMAINING_TIME_UNKNOWN = 0xFFFF


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
        validate_flags(flags, CookingStepStatusFlags, "Cooking Step Status Flags")
        cooking_step_index = DataParser.parse_int16(data, 1, signed=False)
        remaining_time_raw = DataParser.parse_int16(data, 3, signed=False)
        if remaining_time_raw == _REMAINING_TIME_UNKNOWN:
            raise SpecialValueDetectedError(
                special_value=SpecialValueResult(
                    raw_value=_REMAINING_TIME_UNKNOWN,
                    meaning="value is not known",
                    value_type=SpecialValueType.UNKNOWN,
                ),
                name=self.name,
                uuid=self.uuid,
                raw_data=bytes(data),
                raw_int=_REMAINING_TIME_UNKNOWN,
            )
        if remaining_time_raw > _REMAINING_TIME_MAX_SECONDS:
            raise ValueError("Remaining Time uses an RFU value")
        return CookingStepStatusData(
            flags=flags,
            cooking_step_index=cooking_step_index,
            remaining_time_seconds=remaining_time_raw,
        )

    def _encode_value(self, data: CookingStepStatusData) -> bytearray:
        validate_flags(data.flags, CookingStepStatusFlags, "Cooking Step Status Flags")
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.cooking_step_index, signed=False))
        if 0 <= data.remaining_time_seconds <= _REMAINING_TIME_MAX_SECONDS:
            result.extend(DataParser.encode_int16(data.remaining_time_seconds, signed=False))
        else:
            raise ValueError("Remaining Time must be 0x0000-0xFF00")
        return result
