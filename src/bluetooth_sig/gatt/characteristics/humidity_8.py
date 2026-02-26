"""Humidity 8 characteristic (0x2B23)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint8Template


class Humidity8Characteristic(BaseCharacteristic[float]):
    """Humidity 8 characteristic (0x2B23).

    org.bluetooth.characteristic.humidity_8

    Humidity as a percentage with a resolution of 0.5.
    M=1, d=0, b=-1 → scale factor 0.5 (binary exponent 2^-1).
    Range: 0-100%. A value of 0xFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFF).
    """

    _template = ScaledUint8Template(scale_factor=0.5)
