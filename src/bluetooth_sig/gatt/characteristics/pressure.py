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

    # Override template validation for realistic atmospheric pressure range
    max_value: float = 200000.0  # 0 to 2000 hPa (200000 Pa)
    expected_length: int = 4  # uint32
