"""MeshProxySolicitation Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class MeshProxySolicitationService(BaseGattService):
    """Mesh Proxy Solicitation Service implementation (0x1859).

    Enables solicitation of Mesh Proxy nodes to establish GATT
    connections for mesh communication.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
