"""Luminous Intensity characteristic (0x2BF5)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class LuminousIntensityCharacteristic(BaseCharacteristic[int]):
    """Luminous Intensity characteristic (0x2BF5).

    org.bluetooth.characteristic.luminous_intensity

    Luminous intensity in candela with a resolution of 1.
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = Uint16Template()
