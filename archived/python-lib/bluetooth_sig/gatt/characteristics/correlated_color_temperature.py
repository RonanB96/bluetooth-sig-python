"""Correlated Color Temperature characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class CorrelatedColorTemperatureCharacteristic(BaseCharacteristic[int]):
    """Correlated Color Temperature characteristic (0x2AE4).

    org.bluetooth.characteristic.correlated_color_temperature

    Represents correlated color temperature in Kelvin.
    """

    _template = Uint16Template()
