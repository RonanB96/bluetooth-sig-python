"""Temperature characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import TemperatureTemplate


class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature characteristic (0x2A6E).

    org.bluetooth.characteristic.temperature

    Temperature measurement characteristic.
    """

    _template = TemperatureTemplate()
