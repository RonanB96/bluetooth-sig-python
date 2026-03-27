"""Bearer List Current Calls characteristic (0x2BB9)."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CallState(IntEnum):
    """Call state values per TBS specification."""

    INCOMING = 0x00
    DIALING = 0x01
    ALERTING = 0x02
    ACTIVE = 0x03
    LOCALLY_HELD = 0x04
    REMOTELY_HELD = 0x05
    LOCALLY_AND_REMOTELY_HELD = 0x06


class CallFlags(IntFlag):
    """Call flags per TBS specification."""

    INCOMING = 0x01
    WITHHELD = 0x02
    WITHHELD_BY_NETWORK = 0x04


class CallListItem(msgspec.Struct, frozen=True, kw_only=True):
    """A single call entry in the Bearer List Current Calls."""

    call_index: int
    state: CallState
    call_flags: CallFlags
    uri: str


class BearerListCurrentCallsData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Bearer List Current Calls characteristic."""

    calls: tuple[CallListItem, ...]


_MIN_ITEM_LENGTH = 3  # call_index (uint8) + call_state (uint8) + call_flags (uint8)


class BearerListCurrentCallsCharacteristic(BaseCharacteristic[BearerListCurrentCallsData]):
    """Bearer List Current Calls characteristic (0x2BB9).

    org.bluetooth.characteristic.bearer_list_current_calls

    List of current calls on the telephone bearer. Each list item
    contains a length prefix, call index, state, flags, and URI.
    """

    min_length = 0
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BearerListCurrentCallsData:
        calls: list[CallListItem] = []
        offset = 0

        while offset < len(data):
            if offset + 1 > len(data):
                break
            item_length = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

            if item_length < _MIN_ITEM_LENGTH or offset + item_length > len(data):
                break

            call_index = DataParser.parse_int8(data, offset, signed=False)
            state = CallState(DataParser.parse_int8(data, offset + 1, signed=False))
            call_flags = CallFlags(DataParser.parse_int8(data, offset + 2, signed=False))

            uri_length = item_length - 3
            uri = ""
            if uri_length > 0:
                uri = DataParser.parse_utf8_string(data[offset + 3 : offset + 3 + uri_length])

            calls.append(
                CallListItem(
                    call_index=call_index,
                    state=state,
                    call_flags=call_flags,
                    uri=uri,
                )
            )
            offset += item_length

        return BearerListCurrentCallsData(calls=tuple(calls))

    def _encode_value(self, data: BearerListCurrentCallsData) -> bytearray:
        result = bytearray()
        for call in data.calls:
            uri_bytes = call.uri.encode("utf-8")
            item_length = 3 + len(uri_bytes)
            result.append(item_length)
            result.extend(DataParser.encode_int8(call.call_index, signed=False))
            result.extend(DataParser.encode_int8(int(call.state), signed=False))
            result.extend(DataParser.encode_int8(int(call.call_flags), signed=False))
            result.extend(uri_bytes)
        return result
