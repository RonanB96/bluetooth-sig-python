"""MeshProxy Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class MeshProxyService(BaseGattService):
    """Mesh Proxy Service implementation (0x1828).

    Enables GATT-based communication with a Bluetooth Mesh network
    via a proxy node.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.MESH_PROXY_DATA_IN: True,
        CharacteristicName.MESH_PROXY_DATA_OUT: True,
    }
