"""InsulinDelivery Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class InsulinDeliveryService(BaseGattService):
    """Insulin Delivery Service implementation (0x183A).

    Used for insulin delivery devices (insulin pumps). Provides
    device features, delivery status, command control, and
    historical data access.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.IDD_STATUS_CHANGED: True,
        CharacteristicName.IDD_STATUS: True,
        CharacteristicName.IDD_ANNUNCIATION_STATUS: True,
        CharacteristicName.IDD_FEATURES: True,
        CharacteristicName.IDD_STATUS_READER_CONTROL_POINT: True,
        CharacteristicName.IDD_COMMAND_CONTROL_POINT: False,
        CharacteristicName.IDD_COMMAND_DATA: False,
        CharacteristicName.IDD_RECORD_ACCESS_CONTROL_POINT: False,
        CharacteristicName.IDD_HISTORY_DATA: False,
    }
