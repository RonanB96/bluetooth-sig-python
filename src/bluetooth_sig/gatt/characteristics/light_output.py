"""Light Output characteristic (0x2BF0)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint24Template


class LightOutputCharacteristic(BaseCharacteristic[int]):
    """Light Output characteristic (0x2BF0).

    org.bluetooth.characteristic.light_output

    Light output in lumens with a resolution of 1.
    A value of 0xFFFFFE represents 'value is not valid'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFE).
    """

    _template = Uint24Template()
