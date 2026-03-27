"""ObjectTransfer Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ObjectTransferService(BaseGattService):
    """Object Transfer Service implementation (0x1825).

    Provides object-based data transfer including browsing, reading,
    writing, and managing objects on a remote device.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.OTS_FEATURE: True,
        CharacteristicName.OBJECT_NAME: False,
        CharacteristicName.OBJECT_TYPE: False,
        CharacteristicName.OBJECT_SIZE: False,
        CharacteristicName.OBJECT_FIRST_CREATED: False,
        CharacteristicName.OBJECT_LAST_MODIFIED: False,
        CharacteristicName.OBJECT_ID: False,
        CharacteristicName.OBJECT_PROPERTIES: False,
        CharacteristicName.OBJECT_ACTION_CONTROL_POINT: False,
        CharacteristicName.OBJECT_LIST_CONTROL_POINT: False,
        CharacteristicName.OBJECT_LIST_FILTER: False,
        CharacteristicName.OBJECT_CHANGED: False,
    }
