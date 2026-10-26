"""HTTPS Security characteristic."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class HttpsSecurityState(IntEnum):
    """HTTPS security protocol state."""

    HTTP = 0
    HTTPS = 1


class HttpsSecurityCharacteristic(BaseCharacteristic[HttpsSecurityState]):
    """HTTPS Security characteristic (0x2ABB).

    org.bluetooth.characteristic.https_security

    Indicates whether HTTPS (1) or HTTP (0) is used for the connection.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(HttpsSecurityState)
