"""Luminous Exposure characteristic (0x2BF3)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint24Template


class LuminousExposureCharacteristic(BaseCharacteristic[int]):
    """Luminous Exposure characteristic (0x2BF3).

    org.bluetooth.characteristic.luminous_exposure

    Luminous exposure in lux hours with a resolution of 1000.
    A value of 0xFFFFFE represents 'value is not valid'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFE).
    """

    _template = Uint24Template()
