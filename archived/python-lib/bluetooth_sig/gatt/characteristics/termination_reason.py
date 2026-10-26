"""Termination Reason characteristic (0x2BC0)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class TerminationReason(IntEnum):
    """Call termination reason as per TBS 1.0, Table 3.14."""

    INVALID_URI = 0x00
    CALL_FAILED = 0x01
    REMOTE_PARTY_ENDED = 0x02
    SERVER_ENDED = 0x03
    LINE_BUSY = 0x04
    NETWORK_CONGESTION = 0x05
    CLIENT_ENDED = 0x06
    NO_SERVICE = 0x07
    NO_ANSWER = 0x08
    UNSPECIFIED = 0x09


class TerminationReasonData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Termination Reason characteristic."""

    call_index: int
    reason: TerminationReason


class TerminationReasonCharacteristic(BaseCharacteristic[TerminationReasonData]):
    """Termination Reason characteristic (0x2BC0).

    org.bluetooth.characteristic.termination_reason

    Call Index (uint8) followed by Reason Code (uint8).

    References:
        Telephone Bearer Service 1.0, Section 3.16
    """

    expected_length: int = 2

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TerminationReasonData:
        call_index = DataParser.parse_int8(data, 0, signed=False)
        reason = TerminationReason(DataParser.parse_int8(data, 1, signed=False))

        return TerminationReasonData(call_index=call_index, reason=reason)

    def _encode_value(self, data: TerminationReasonData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(data.call_index, signed=False))
        result.extend(DataParser.encode_int8(int(data.reason), signed=False))
        return result
