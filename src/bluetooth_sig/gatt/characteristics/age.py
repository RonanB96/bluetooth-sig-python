"""Age characteristic (0x2A80)."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.templates import Uint8Template

from .base import BaseCharacteristic


class AgeCharacteristic(BaseCharacteristic[int]):
    """Age characteristic (0x2A80).

    org.bluetooth.characteristic.age

    Age characteristic.
    """

    _template = Uint8Template()
