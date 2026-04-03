"""HTTP Headers characteristic (0x2AB7)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class HTTPHeadersCharacteristic(BaseCharacteristic[str]):
    """HTTP Headers characteristic (0x2AB7).

    org.bluetooth.characteristic.http_headers

    Contains the HTTP headers of an HTTP message.
    """

    _template = Utf8StringTemplate()
    min_length = 0
