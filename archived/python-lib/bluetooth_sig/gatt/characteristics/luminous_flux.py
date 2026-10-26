"""Luminous Flux characteristic (0x2BF4)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class LuminousFluxCharacteristic(BaseCharacteristic[int]):
    """Luminous Flux characteristic (0x2BF4).

    org.bluetooth.characteristic.luminous_flux

    Luminous flux in lumens with a resolution of 1.
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = Uint16Template()
