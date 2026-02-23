"""Luminous Efficacy characteristic (0x2BF6)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class LuminousEfficacyCharacteristic(BaseCharacteristic[float]):
    """Luminous Efficacy characteristic (0x2BF6).

    org.bluetooth.characteristic.luminous_efficacy

    Luminous efficacy in lumens per watt with a resolution of 0.1.
    M=1, d=-1, b=0 → scale factor 0.1.
    Range: 0-1800. A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-1, b=0)
