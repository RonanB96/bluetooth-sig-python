"""Luminous Energy characteristic (0x2BF2)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint24Template


class LuminousEnergyCharacteristic(BaseCharacteristic[int]):
    """Luminous Energy characteristic (0x2BF2).

    org.bluetooth.characteristic.luminous_energy

    Luminous energy in lumen hours with a resolution of 1000.
    A value of 0xFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFF).
    """

    _template = Uint24Template()
