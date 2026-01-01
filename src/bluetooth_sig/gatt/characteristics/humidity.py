"""Humidity characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HumidityCharacteristic(BaseCharacteristic):
    """Humidity characteristic (0x2A6F).

    org.bluetooth.characteristic.humidity

    Humidity measurement characteristic.
    """

    # Template configuration
    _template = ScaledUint16Template(scale_factor=0.01)
