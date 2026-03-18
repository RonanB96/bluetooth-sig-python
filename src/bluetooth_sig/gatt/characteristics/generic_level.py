"""Generic Level characteristic (0x2AF9)."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint16Template


class GenericLevelCharacteristic(BaseCharacteristic[int]):
    """Generic Level characteristic (0x2AF9).

    org.bluetooth.characteristic.generic_level

    Unitless 16-bit level value (0-65535).
    """

    _manual_role = CharacteristicRole.MEASUREMENT
    _template = Uint16Template()
