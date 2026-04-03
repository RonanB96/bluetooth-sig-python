"""Incoming Call Target Bearer URI characteristic (0x2BC2)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IncomingCallTargetBearerURIData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Incoming Call Target Bearer URI characteristic."""

    call_index: int
    uri: str


class IncomingCallTargetBearerURICharacteristic(BaseCharacteristic[IncomingCallTargetBearerURIData]):
    """Incoming Call Target Bearer URI characteristic (0x2BC2).

    org.bluetooth.characteristic.incoming_call_target_bearer_uri

    Provides the URI of the target bearer for an incoming call.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IncomingCallTargetBearerURIData:
        call_index = DataParser.parse_int8(data, 0, signed=False)
        uri = DataParser.parse_utf8_string(data[1:]) if len(data) > 1 else ""

        return IncomingCallTargetBearerURIData(call_index=call_index, uri=uri)

    def _encode_value(self, data: IncomingCallTargetBearerURIData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(data.call_index, signed=False))
        result.extend(data.uri.encode("utf-8"))
        return result
