"""Irradiance characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class IrradianceCharacteristic(BaseCharacteristic[float]):
    """Irradiance characteristic (0x2A77).

    org.bluetooth.characteristic.irradiance

    Represents irradiance in W/m² with 0.1 resolution (M=1, d=-1, b=0).
    """

    _template = ScaledUint16Template(scale_factor=0.1)
