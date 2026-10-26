"""Energy characteristic (0x2AF1)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint24Template


class EnergyCharacteristic(BaseCharacteristic[int]):
    """Energy characteristic (0x2AF1).

    org.bluetooth.characteristic.energy

    Energy in kilowatt-hours with a resolution of 1.
    A value of 0xFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFF).
    """

    _template = Uint24Template()
