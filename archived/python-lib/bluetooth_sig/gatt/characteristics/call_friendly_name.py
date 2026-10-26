"""Call Friendly Name characteristic (0x2BC2)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CallFriendlyNameData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Call Friendly Name characteristic."""

    call_index: int
    friendly_name: str


class CallFriendlyNameCharacteristic(BaseCharacteristic[CallFriendlyNameData]):
    """Call Friendly Name characteristic (0x2BC2).

    org.bluetooth.characteristic.call_friendly_name

    Call Index (uint8) followed by a UTF-8 friendly name string.

    References:
        Telephone Bearer Service 1.0, Section 3.15
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CallFriendlyNameData:
        call_index = DataParser.parse_int8(data, 0, signed=False)
        friendly_name = DataParser.parse_utf8_string(data[1:]) if len(data) > 1 else ""

        return CallFriendlyNameData(call_index=call_index, friendly_name=friendly_name)

    def _encode_value(self, data: CallFriendlyNameData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(data.call_index, signed=False))
        result.extend(data.friendly_name.encode("utf-8"))
        return result
