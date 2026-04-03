"""BSS Control Point characteristic (0x2B2B).

Control point for the Binary Sensor Service.

The BSS protocol uses Split Header + Payload format. Messages contain
a Message ID, Number of Parameters, and TLV-encoded parameters.

References:
    Bluetooth SIG Binary Sensor Service 1.0, Sections 3.1 and 4
"""

from __future__ import annotations

import msgspec

from ...types.bss import SplitHeader
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BSSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from BSS Control Point.

    Attributes:
        split_header: Parsed Split Header fields.
        payload: Raw payload bytes (message content). Empty if none.

    """

    split_header: SplitHeader
    payload: bytes = b""


class BSSControlPointCharacteristic(BaseCharacteristic[BSSControlPointData]):
    """BSS Control Point characteristic (0x2B2B).

    org.bluetooth.characteristic.bss_control_point

    Receives commands for the Binary Sensor Service using Split Header +
    Payload format.

    Command message IDs are defined in ``BSSMessageID``:
    ``GET_SENSOR_STATUS_COMMAND`` and ``SETTING_SENSOR_COMMAND``.
    """

    min_length = 1
    max_length = 20
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BSSControlPointData:
        """Parse BSS Control Point data.

        Format: Split Header (uint8) + Payload (1-19 octets).
        """
        raw_header = DataParser.parse_int8(data, 0, signed=False)
        split_header = SplitHeader.from_byte(raw_header)
        payload = bytes(data[1:])

        return BSSControlPointData(
            split_header=split_header,
            payload=payload,
        )

    def _encode_value(self, data: BSSControlPointData) -> bytearray:
        """Encode BSS Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.split_header.to_byte(), signed=False))
        result.extend(data.payload)
        return result
