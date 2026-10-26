"""Length characteristic (0x2C0A)."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint32Template


class LengthCharacteristic(BaseCharacteristic[int]):
    """Length characteristic (0x2C0A).

    org.bluetooth.characteristic.length

    Length measurement in units of 1e-7 metres (100 nm resolution).
    """

    _manual_role = CharacteristicRole.MEASUREMENT
    _template = Uint32Template()
