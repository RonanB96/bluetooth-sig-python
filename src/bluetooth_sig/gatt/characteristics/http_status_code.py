"""HTTP Status Code characteristic (0x2AB8)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class HTTPDataStatus(IntFlag):
    """HTTP data status flags."""

    HEADERS_RECEIVED = 0x01
    HEADERS_TRUNCATED = 0x02
    BODY_RECEIVED = 0x04
    BODY_TRUNCATED = 0x08


class HTTPStatusCodeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from HTTP Status Code characteristic."""

    status_code: int
    data_status: HTTPDataStatus


class HTTPStatusCodeCharacteristic(BaseCharacteristic[HTTPStatusCodeData]):
    """HTTP Status Code characteristic (0x2AB8).

    org.bluetooth.characteristic.http_status_code

    Reports the HTTP status code and data status of the last HTTP operation.
    """

    expected_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> HTTPStatusCodeData:
        status_code = DataParser.parse_int16(data, 0, signed=False)
        data_status = HTTPDataStatus(DataParser.parse_int8(data, 2, signed=False))

        return HTTPStatusCodeData(
            status_code=status_code,
            data_status=data_status,
        )

    def _encode_value(self, data: HTTPStatusCodeData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(data.status_code, signed=False))
        result.extend(DataParser.encode_int8(int(data.data_status), signed=False))
        return result
