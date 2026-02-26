"""High Temperature characteristic (0x2A45)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class HighTemperatureCharacteristic(BaseCharacteristic[float]):
    """High Temperature characteristic (0x2A45).

    org.bluetooth.characteristic.high_temperature

    Temperature in degrees Celsius with a resolution of 0.5.
    M=1, d=0, b=-1 → scale factor 0.5 (binary exponent 2^-1).
    A value of 0x8001 represents 'value is not valid'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x8001).
    """

    _template = ScaledSint16Template(scale_factor=0.5)
