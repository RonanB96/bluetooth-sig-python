"""Incoming Call characteristic (0x2BC1)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IncomingCallData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Incoming Call characteristic."""

    call_index: int
    uri: str


class IncomingCallCharacteristic(BaseCharacteristic[IncomingCallData]):
    """Incoming Call characteristic (0x2BC1).

    org.bluetooth.characteristic.incoming_call

    Notifies the client of an incoming call with the caller URI.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IncomingCallData:
        call_index = DataParser.parse_int8(data, 0, signed=False)
        uri = DataParser.parse_utf8_string(data[1:]) if len(data) > 1 else ""

        return IncomingCallData(call_index=call_index, uri=uri)

    def _encode_value(self, data: IncomingCallData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(data.call_index, signed=False))
        result.extend(data.uri.encode("utf-8"))
        return result
