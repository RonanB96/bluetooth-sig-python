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

    _service_name: str | None = "HTTP Proxy"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.URI: True,
        CharacteristicName.HTTP_HEADERS: True,
        CharacteristicName.HTTP_ENTITY_BODY: True,
        CharacteristicName.HTTP_CONTROL_POINT: True,
        CharacteristicName.HTTP_STATUS_CODE: True,
        CharacteristicName.HTTPS_SECURITY: True,
    }
