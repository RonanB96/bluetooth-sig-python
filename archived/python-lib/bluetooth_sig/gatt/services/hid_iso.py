"""HidIso Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class HidIsoService(BaseGattService):
    """HID ISO Service implementation (0x185C).

    Provides Human Interface Device functionality over LE Audio
    isochronous channels for low-latency input.
    """

    _service_name: str = "HID ISO"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HID_ISO_PROPERTIES: False,
        CharacteristicName.LE_HID_OPERATION_MODE: False,
    }
