"""ACS Data Out Indicate characteristic (0x2B32)."""

from __future__ import annotations

from ...types import MAX_ROLLING_SEGMENT_COUNTER, ACSDataPacket, ACSSegmentationHeader
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ACSDataOutIndicateCharacteristic(BaseCharacteristic[ACSDataPacket]):
    """ACS Data Out Indicate characteristic (0x2B32).

    org.bluetooth.characteristic.acs_data_out_indicate

    Segmented indicated data output for Authorization Control Service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ACSDataPacket:
        header = DataParser.parse_int8(data, 0, signed=False)
        payload = bytes(data[1:])

        return ACSDataPacket(
            header=ACSSegmentationHeader(
                first_segment=bool(header & 0x01),
                last_segment=bool(header & 0x02),
                rolling_segment_counter=(header >> 2) & 0x3F,
            ),
            payload=payload,
        )

    def _encode_value(self, data: ACSDataPacket) -> bytearray:
        counter = data.header.rolling_segment_counter
        if not 0 <= counter <= MAX_ROLLING_SEGMENT_COUNTER:
            raise ValueError(f"rolling_segment_counter must be in range 0-63, got {counter}")

        header = 0
        if data.header.first_segment:
            header |= 0x01
        if data.header.last_segment:
            header |= 0x02

        header |= counter << 2
        return bytearray([header, *data.payload])
