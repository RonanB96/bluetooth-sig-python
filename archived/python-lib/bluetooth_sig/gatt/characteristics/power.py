"""Power characteristic (0x2B05)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint24Template


class PowerCharacteristic(BaseCharacteristic[float]):
    """Power characteristic (0x2B05).

    org.bluetooth.characteristic.power

    Power in watts with a resolution of 0.1.
    M=1, d=-1, b=0 → scale factor 0.1.
    Range: 0-1677721.3 W. A value of 0xFFFFFE represents 'value is not valid'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFE).
    """

    _template = ScaledUint24Template.from_letter_method(M=1, d=-1, b=0)
