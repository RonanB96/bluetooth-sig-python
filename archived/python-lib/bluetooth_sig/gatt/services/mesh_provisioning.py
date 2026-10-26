"""MeshProvisioning Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class MeshProvisioningService(BaseGattService):
    """Mesh Provisioning Service implementation (0x1827).

    Provides the provisioning interface for adding devices to a
    Bluetooth Mesh network.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.MESH_PROVISIONING_DATA_IN: True,
        CharacteristicName.MESH_PROVISIONING_DATA_OUT: True,
    }
