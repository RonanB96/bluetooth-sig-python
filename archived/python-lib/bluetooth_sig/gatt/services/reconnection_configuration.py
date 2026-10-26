"""ReconnectionConfiguration Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ReconnectionConfigurationService(BaseGattService):
    """Reconnection Configuration Service implementation (0x1829).

    Allows a client to configure reconnection parameters on a
    peripheral device.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.RC_FEATURE: True,
        CharacteristicName.RC_SETTINGS: False,
        CharacteristicName.RECONNECTION_CONFIGURATION_CONTROL_POINT: False,
    }
