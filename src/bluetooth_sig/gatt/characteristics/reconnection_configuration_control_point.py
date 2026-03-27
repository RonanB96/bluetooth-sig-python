"""Reconnection Configuration Control Point characteristic (0x2B1F)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ReconnectionConfigurationOpCode(IntEnum):
    """Reconnection Configuration Control Point opcodes."""

    ENABLE_DISCONNECT = 0x00
    ENABLE_RECONNECT = 0x01
    CANCEL_RECONNECT = 0x02


class ReconnectionConfigurationControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Reconnection Configuration Control Point."""

    op_code: ReconnectionConfigurationOpCode
    parameter: bytes | None = None


class ReconnectionConfigurationControlPointCharacteristic(
    BaseCharacteristic[ReconnectionConfigurationControlPointData],
):
    """Reconnection Configuration Control Point characteristic (0x2B1F).

    org.bluetooth.characteristic.reconnection_configuration_control_point

    Used to configure reconnection behaviour of the device.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ReconnectionConfigurationControlPointData:
        op_code = ReconnectionConfigurationOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:]) if len(data) > 1 else None

        return ReconnectionConfigurationControlPointData(
            op_code=op_code,
            parameter=parameter,
        )

    def _encode_value(self, data: ReconnectionConfigurationControlPointData) -> bytearray:
        result = bytearray([int(data.op_code)])
        if data.parameter is not None:
            result.extend(data.parameter)
        return result
