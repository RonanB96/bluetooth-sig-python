"""Device Time Control Point characteristic (0x2B91)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DeviceTimeControlPointOpCode(IntEnum):
    """Device Time Control Point operation codes."""

    GET_DEVICE_TIME = 0x01
    SET_DEVICE_TIME = 0x02
    CANCEL_OPERATION = 0x03


class DeviceTimeControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time Control Point characteristic."""

    op_code: DeviceTimeControlPointOpCode
    parameter: bytes | None = None


class DeviceTimeControlPointCharacteristic(BaseCharacteristic[DeviceTimeControlPointData]):
    """Device Time Control Point characteristic (0x2B91).

    org.bluetooth.characteristic.device_time_control_point

    Used to control the Device Time service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DeviceTimeControlPointData:
        op_code = DeviceTimeControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:]) if len(data) > 1 else None

        return DeviceTimeControlPointData(op_code=op_code, parameter=parameter)

    def _encode_value(self, data: DeviceTimeControlPointData) -> bytearray:
        result = bytearray([int(data.op_code)])
        if data.parameter is not None:
            result.extend(data.parameter)
        return result
