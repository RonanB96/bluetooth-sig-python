"""TransportDiscovery Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class TransportDiscoveryService(BaseGattService):
    """Transport Discovery Service implementation (0x1824).

    Enables discovery of transport information for establishing
    connections over alternative transports (e.g., Wi-Fi, classic BT).
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TDS_CONTROL_POINT: False,
        CharacteristicName.BR_EDR_HANDOVER_DATA: False,
        CharacteristicName.BLUETOOTH_SIG_DATA: False,
    }
