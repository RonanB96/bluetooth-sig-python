"""EmergencyConfiguration Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class EmergencyConfigurationService(BaseGattService):
    """Emergency Configuration Service implementation (0x183C).

    Configures emergency identification and messaging capabilities
    for BLE devices.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.EMERGENCY_ID: False,
        CharacteristicName.EMERGENCY_TEXT: False,
    }
