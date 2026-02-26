"""Generic Level characteristic (0x2AF9)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class GenericLevelCharacteristic(BaseCharacteristic[int]):
    """Generic Level characteristic (0x2AF9).

    org.bluetooth.characteristic.generic_level

    Unitless 16-bit level value (0-65535).
    """

    _template = Uint16Template()
