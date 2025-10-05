"""Apparent Wind Speed characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ApparentWindSpeedCharacteristic(BaseCharacteristic):
    """Apparent Wind Speed measurement characteristic."""

    _template = ScaledUint16Template()
