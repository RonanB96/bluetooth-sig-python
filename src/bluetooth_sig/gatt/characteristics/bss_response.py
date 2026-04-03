"""BSS Response characteristic (0x2B2C).

Response characteristic for the Binary Sensor Service.

The BSS protocol uses Split Header + Payload format. Responses and
unsolicited events are indicated via this characteristic.

References:
    Bluetooth SIG Binary Sensor Service 1.0, Sections 3.2 and 4
"""

from __future__ import annotations

import msgspec

from ...types.bss import SplitHeader
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BSSResponseData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from BSS Response.

    Attributes:
        split_header: Parsed Split Header fields.
        payload: Raw payload bytes (message content). Empty if none.

    """

    split_header: SplitHeader
    payload: bytes = b""


class BSSResponseCharacteristic(BaseCharacteristic[BSSResponseData]):
    """BSS Response characteristic (0x2B2C).

    org.bluetooth.characteristic.bss_response

    Sends responses and unsolicited events from the Binary Sensor
    Service using Split Header + Payload format.

    Response message IDs are defined in ``BSSMessageID``:
    ``GET_SENSOR_STATUS_RESPONSE``, ``SETTING_SENSOR_RESPONSE``,
    and ``SENSOR_STATUS_EVENT``.
    """

    min_length = 1
    max_length = 20
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BSSResponseData:
        """Parse BSS Response data.

        Format: Split Header (uint8) + Payload (1-19 octets).
        """
        raw_header = DataParser.parse_int8(data, 0, signed=False)
        split_header = SplitHeader.from_byte(raw_header)
        payload = bytes(data[1:])

        return BSSResponseData(
            split_header=split_header,
            payload=payload,
        )

    def _encode_value(self, data: BSSResponseData) -> bytearray:
        """Encode BSS Response data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.split_header.to_byte(), signed=False))
        result.extend(data.payload)
        return result
