"""HTTP Entity Body characteristic (0x2AB9)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class HTTPEntityBodyCharacteristic(BaseCharacteristic[str]):
    """HTTP Entity Body characteristic (0x2AB9).

    org.bluetooth.characteristic.http_entity_body

    Contains the body content of an HTTP message.
    """

    _template = Utf8StringTemplate()
    min_length = 0
