"""Mass Flow characteristic (0x2C17)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class MassFlowCharacteristic(BaseCharacteristic[int]):
    """Mass Flow characteristic (0x2C17).

    org.bluetooth.characteristic.mass_flow

    Mass flow in grams per second with a resolution of 1.
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = Uint16Template()
