"""ACS Control Point characteristic (0x2B33)."""

from __future__ import annotations

from ...types import MAX_ROLLING_SEGMENT_COUNTER, ACSControlPointData, ACSSegmentationHeader
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ACSControlPointCharacteristic(BaseCharacteristic[ACSControlPointData]):
    """ACS Control Point characteristic (0x2B33).

    org.bluetooth.characteristic.acs_control_point

    Segmented control point for Authorization Control Service operations.
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ACSControlPointData:
        """Parse ACS Control Point data.

        Format: Segmentation Header (uint8) + OpCode (uint8) + Operand (variable).
        """
        header = DataParser.parse_int8(data, 0, signed=False)
        opcode = DataParser.parse_int8(data, 1, signed=False)
        operand = bytes(data[2:])

        return ACSControlPointData(
            header=ACSSegmentationHeader(
                first_segment=bool(header & 0x01),
                last_segment=bool(header & 0x02),
                rolling_segment_counter=(header >> 2) & 0x3F,
            ),
            opcode=opcode,
            operand=operand,
        )

    def _encode_value(self, data: ACSControlPointData) -> bytearray:
        """Encode ACS Control Point data."""
        counter = data.header.rolling_segment_counter
        if not 0 <= counter <= MAX_ROLLING_SEGMENT_COUNTER:
            raise ValueError(f"rolling_segment_counter must be in range 0-63, got {counter}")

        header = 0
        if data.header.first_segment:
            header |= 0x01
        if data.header.last_segment:
            header |= 0x02

        header |= counter << 2

        result = bytearray()
        result.extend(DataParser.encode_int8(header, signed=False))
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.operand)
        return result
