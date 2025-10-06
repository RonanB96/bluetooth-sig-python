"""Temperature characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import TemperatureTemplate


class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature measurement characteristic."""

    _template = TemperatureTemplate()

    _characteristic_name: str = "Temperature"
