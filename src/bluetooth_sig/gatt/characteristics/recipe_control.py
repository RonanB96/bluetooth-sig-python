"""Recipe Control characteristic (0x2C26)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..constants import SIZE_UINT8
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RecipeControlOpCode(IntEnum):
    """Recipe Control operation codes."""

    READ = 0x00
    START = 0x01
    STOP = 0x02
    DELETE = 0x03


class RecipeControlData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Recipe Control payload."""

    op_code: RecipeControlOpCode
    cooking_step_index: int | None = None


class RecipeControlCharacteristic(BaseCharacteristic[RecipeControlData]):
    """Recipe Control characteristic (0x2C26).

    org.bluetooth.characteristic.recipe_control
    """

    min_length = SIZE_UINT8
    max_length = 3
    allow_variable_length = True
    _FULL_PAYLOAD_LENGTH = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RecipeControlData:
        if len(data) not in {SIZE_UINT8, self._FULL_PAYLOAD_LENGTH}:
            raise ValueError("Recipe Control payload must be 1 or 3 bytes")

        op_code = RecipeControlOpCode(DataParser.parse_int8(data, 0, signed=False))
        cooking_step_index = (
            DataParser.parse_int16(data, SIZE_UINT8, signed=False) if len(data) == self._FULL_PAYLOAD_LENGTH else None
        )
        return RecipeControlData(op_code=op_code, cooking_step_index=cooking_step_index)

    def _encode_value(self, data: RecipeControlData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.op_code), signed=False))
        if data.cooking_step_index is not None:
            result.extend(DataParser.encode_int16(data.cooking_step_index, signed=False))
        return result
