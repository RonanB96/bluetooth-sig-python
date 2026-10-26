"""InternetProtocolSupport Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class InternetProtocolSupportService(BaseGattService):
    """Internet Protocol Support Service implementation (0x1820).

    Enables IPv6 communication over Bluetooth Low Energy (IPSP).
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
