"""Cosine of the Angle characteristic (0x2AE8)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint8Template


class CosineOfTheAngleCharacteristic(BaseCharacteristic[float]):
    """Cosine of the Angle characteristic (0x2AE8).

    org.bluetooth.characteristic.cosine_of_the_angle

    Unitless cosine value expressed as cos(theta) x 100.
    M=1, d=-2, b=0 -> resolution 0.01 (-1.00 to 1.00).
    A raw value of 0x7F represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x7F).
    """

    _template = ScaledSint8Template.from_letter_method(M=1, d=-2, b=0)
