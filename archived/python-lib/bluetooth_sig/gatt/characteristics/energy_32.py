"""Energy 32 characteristic (0x2AF2)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint32Template


class Energy32Characteristic(BaseCharacteristic[int]):
    """Energy 32 characteristic (0x2AF2).

    org.bluetooth.characteristic.energy_32

    Energy in watt-hours with a resolution of 1 Wh.
    A value of 0xFFFFFFFE represents 'value is not valid'.
    A value of 0xFFFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFFFF).
    """

    _template = Uint32Template()
