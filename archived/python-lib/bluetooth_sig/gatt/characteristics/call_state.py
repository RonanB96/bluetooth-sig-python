"""Call State characteristic (0x2BBC)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .bearer_list_current_calls import CallFlags, CallState

_CALL_STATE_ENTRY_SIZE = 3  # call_index(1) + state(1) + flags(1)


class CallStateEntry(msgspec.Struct, frozen=True, kw_only=True):
    """A single call state entry."""

    call_index: int
    state: CallState
    call_flags: CallFlags


class CallStateData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Call State characteristic."""

    entries: tuple[CallStateEntry, ...]


class CallStateCharacteristic(BaseCharacteristic[CallStateData]):
    """Call State characteristic (0x2BBC).

    org.bluetooth.characteristic.call_state

    List of call states for all current calls.
    """

    min_length = 0
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CallStateData:
        entries: list[CallStateEntry] = []
        offset = 0

        while offset + _CALL_STATE_ENTRY_SIZE <= len(data):
            call_index = data[offset]
            state = CallState(data[offset + 1])
            call_flags = CallFlags(data[offset + 2])
            entries.append(
                CallStateEntry(
                    call_index=call_index,
                    state=state,
                    call_flags=call_flags,
                )
            )
            offset += _CALL_STATE_ENTRY_SIZE

        return CallStateData(entries=tuple(entries))

    def _encode_value(self, data: CallStateData) -> bytearray:
        result = bytearray()
        for entry in data.entries:
            result.append(entry.call_index)
            result.append(int(entry.state))
            result.append(int(entry.call_flags))
        return result
