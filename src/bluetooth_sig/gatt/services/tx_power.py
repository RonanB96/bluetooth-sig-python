"""Tx Power Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class TxPowerService(BaseGattService):
    """Tx Power Service implementation.

    Exposes the current transmit power level of a device.

    Contains characteristics related to transmit power:
    - Tx Power Level - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TX_POWER_LEVEL: True,  # required
    }
