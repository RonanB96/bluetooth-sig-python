"""Illuminance 16 characteristic (0x2C15)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class Illuminance16Characteristic(BaseCharacteristic[int]):
    """Illuminance 16 characteristic (0x2C15).

    org.bluetooth.characteristic.illuminance_16

    Illuminance in lux with a resolution of 1.
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = Uint16Template()
