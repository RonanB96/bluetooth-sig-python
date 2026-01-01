"""Pressure characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import PressureTemplate


class PressureCharacteristic(BaseCharacteristic):
    """Pressure characteristic (0x2A6D).

    org.bluetooth.characteristic.pressure

    Atmospheric pressure characteristic.
    """

    _template = PressureTemplate()
