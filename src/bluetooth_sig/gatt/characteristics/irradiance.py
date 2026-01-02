"""Irradiance characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class IrradianceCharacteristic(BaseCharacteristic):
    """Irradiance characteristic (0x2A77).

    org.bluetooth.characteristic.irradiance

    Represents irradiance as an unsigned 16-bit integer.
    """

    _template = Uint16Template()
