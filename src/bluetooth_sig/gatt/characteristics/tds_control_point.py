"""TDS Control Point characteristic (0x2ABC)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class TDSControlPointOpCode(IntEnum):
    """TDS Control Point operation codes."""

    ACTIVATE_TRANSPORT = 0x01


_PARAMETER_START_INDEX = 2


class TDSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from TDS Control Point characteristic."""

    op_code: TDSControlPointOpCode
    organization_id: int
    parameter: bytes | None = None


class TDSControlPointCharacteristic(BaseCharacteristic[TDSControlPointData]):
    """TDS Control Point characteristic (0x2ABC).

    org.bluetooth.characteristic.tds_control_point

    Used to activate a transport on the Transport Discovery Service.
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TDSControlPointData:
        op_code = TDSControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        organization_id = DataParser.parse_int8(data, 1, signed=False)
        parameter = bytes(data[_PARAMETER_START_INDEX:]) if len(data) > _PARAMETER_START_INDEX else None

        return TDSControlPointData(
            op_code=op_code,
            organization_id=organization_id,
            parameter=parameter,
        )

    def _encode_value(self, data: TDSControlPointData) -> bytearray:
        result = bytearray()
        result.append(int(data.op_code))
        result.extend(DataParser.encode_int8(data.organization_id, signed=False))
        if data.parameter is not None:
            result.extend(data.parameter)
        return result
