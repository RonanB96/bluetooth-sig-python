"""Pressure characteristic implementation."""

from dataclasses import dataclass

from .templates import PressureCharacteristic as PressureTemplate


@dataclass
class PressureCharacteristic(PressureTemplate):
    """Atmospheric pressure characteristic."""

    _characteristic_name: str = "Pressure"

    # Override template validation for realistic atmospheric pressure range
    max_value: float = 200000.0  # 0 to 2000 hPa (200000 Pa)
