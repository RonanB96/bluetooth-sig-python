"""Temperature 8 characteristic (0x2B0D)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint8Template


class Temperature8Characteristic(BaseCharacteristic[float]):
    """Temperature 8 characteristic (0x2B0D).

    org.bluetooth.characteristic.temperature_8

    Temperature in degrees Celsius with a resolution of 0.5.
    M=1, d=0, b=-1 → scale factor 0.5 (binary exponent 2^-1).
    Range: -64.0 to 63.0. A value of 0x7F represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x7F).
    """

    _template = ScaledSint8Template(scale_factor=0.5)
