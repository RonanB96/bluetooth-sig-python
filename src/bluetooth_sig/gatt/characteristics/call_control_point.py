"""Call Control Point characteristic (0x2BBE)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CallControlPointOpCode(IntEnum):
    """Call Control Point operation codes per TBS specification."""

    ACCEPT = 0x00
    TERMINATE = 0x01
    LOCAL_HOLD = 0x02
    LOCAL_RETRIEVE = 0x03
    ORIGINATE = 0x04
    JOIN = 0x05


class CallControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Call Control Point characteristic.

    For ACCEPT/TERMINATE/LOCAL_HOLD/LOCAL_RETRIEVE: call_index is set.
    For ORIGINATE: uri is set.
    For JOIN: call_indexes is set.
    """

    op_code: CallControlPointOpCode
    call_index: int | None = None
    uri: str | None = None
    call_indexes: tuple[int, ...] | None = None


class CallControlPointCharacteristic(BaseCharacteristic[CallControlPointData]):
    """Call Control Point characteristic (0x2BBE).

    org.bluetooth.characteristic.call_control_point

    Used to control calls on the telephone bearer.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CallControlPointData:
        op_code = CallControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))

        if op_code in (
            CallControlPointOpCode.ACCEPT,
            CallControlPointOpCode.TERMINATE,
            CallControlPointOpCode.LOCAL_HOLD,
            CallControlPointOpCode.LOCAL_RETRIEVE,
        ):
            call_index = DataParser.parse_int8(data, 1, signed=False) if len(data) > 1 else None
            return CallControlPointData(op_code=op_code, call_index=call_index)

        if op_code == CallControlPointOpCode.ORIGINATE:
            uri = DataParser.parse_utf8_string(data[1:]) if len(data) > 1 else None
            return CallControlPointData(op_code=op_code, uri=uri)

        if op_code == CallControlPointOpCode.JOIN:
            indexes = tuple(data[i] for i in range(1, len(data)))
            return CallControlPointData(op_code=op_code, call_indexes=indexes)

        return CallControlPointData(op_code=op_code)

    def _encode_value(self, data: CallControlPointData) -> bytearray:
        result = bytearray([int(data.op_code)])

        if data.call_index is not None:
            result.extend(DataParser.encode_int8(data.call_index, signed=False))
        elif data.uri is not None:
            result.extend(data.uri.encode("utf-8"))
        elif data.call_indexes is not None:
            for idx in data.call_indexes:
                result.append(idx)

        return result
