"""Pressure characteristic implementation."""

from .base import BaseCharacteristic
from .templates import PressureTemplate


class PressureCharacteristic(BaseCharacteristic):
    """Atmospheric pressure characteristic."""

    _template = PressureTemplate()

    _characteristic_name: str = "Pressure"

    # Override template validation for realistic atmospheric pressure range
    max_value: float = 200000.0  # 0 to 2000 hPa (200000 Pa)
