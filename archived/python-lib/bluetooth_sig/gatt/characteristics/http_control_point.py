"""HTTP Control Point characteristic (0x2ABA)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class HTTPControlPointOpCode(IntEnum):
    """HTTP Control Point operation codes per HPS specification."""

    HTTP_GET_REQUEST = 0x01
    HTTP_HEAD_REQUEST = 0x02
    HTTP_POST_REQUEST = 0x03
    HTTP_PUT_REQUEST = 0x04
    HTTP_DELETE_REQUEST = 0x05
    HTTPS_GET_REQUEST = 0x06
    HTTPS_HEAD_REQUEST = 0x07
    HTTPS_POST_REQUEST = 0x08
    HTTPS_PUT_REQUEST = 0x09
    HTTPS_DELETE_REQUEST = 0x0A
    HTTP_REQUEST_CANCEL = 0x0B


class HTTPControlPointCharacteristic(BaseCharacteristic[HTTPControlPointOpCode]):
    """HTTP Control Point characteristic (0x2ABA).

    org.bluetooth.characteristic.http_control_point

    Used to initiate HTTP requests on the HTTP Proxy Service.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(HTTPControlPointOpCode)
