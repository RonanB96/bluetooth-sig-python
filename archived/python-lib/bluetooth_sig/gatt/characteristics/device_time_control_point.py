"""Device Time Control Point characteristic (0x2B91).

Per DTS v1.0 Table 3.14 and Table 3.15, the DTCP characteristic structure is:
  E2E_CRC (uint16, conditional) + Opcode (uint8) + Operand (0-17 bytes).

Request opcodes (Client -> Server):
  0x02: Propose Time Update (M)            — Time Update operand (Table 3.16)
  0x03: Force Time Update (O)              — Time Update operand (Table 3.16)
  0x04: Propose Non-Logged Time Adj Limit  — uint16 operand (Table 3.18)
  0x05: Retrieve Active Time Adjustments   — no operand

Response opcodes (Server -> Client):
  0x07: Report Active Time Adjustments     — operand (Table 3.19)
  0x09: DTCP Response (M)                  — operand (Table 3.20)

Opcodes 0x00, 0x01, 0x06, 0x08, 0x0A-0xFF are Reserved for Future Use.

References:
    Bluetooth SIG Device Time Service v1.0, Table 3.14, Table 3.15
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DeviceTimeControlPointOpCode(IntEnum):
    """DTCP opcode values — DTS v1.0 Table 3.15."""

    PROPOSE_TIME_UPDATE = 0x02
    FORCE_TIME_UPDATE = 0x03
    PROPOSE_NON_LOGGED_TIME_ADJUSTMENT_LIMIT = 0x04
    RETRIEVE_ACTIVE_TIME_ADJUSTMENTS = 0x05
    REPORT_ACTIVE_TIME_ADJUSTMENTS = 0x07
    DTCP_RESPONSE = 0x09


class DeviceTimeControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time Control Point characteristic."""

    op_code: DeviceTimeControlPointOpCode
    parameter: bytes | None = None


class DeviceTimeControlPointCharacteristic(BaseCharacteristic[DeviceTimeControlPointData]):
    """Device Time Control Point characteristic (0x2B91).

    org.bluetooth.characteristic.device_time_control_point

    Used to initiate DTCP procedures on the Device Time Service server.
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
