"""HttpProxy Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class HttpProxyService(BaseGattService):
    """HTTP Proxy Service implementation (0x1823).

    Enables a BLE device to act as an HTTP proxy, allowing
    constrained devices to make HTTP requests via a gateway.
    """

    _service_name: str = "HTTP Proxy"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.URI: False,
        CharacteristicName.HTTP_HEADERS: False,
        CharacteristicName.HTTP_ENTITY_BODY: False,
        CharacteristicName.HTTP_CONTROL_POINT: False,
        CharacteristicName.HTTP_STATUS_CODE: False,
        CharacteristicName.HTTPS_SECURITY: False,
    }
