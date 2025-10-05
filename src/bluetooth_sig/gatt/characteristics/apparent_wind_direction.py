"""Apparent Wind Direction characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ApparentWindDirectionCharacteristic(BaseCharacteristic):
    """Apparent Wind Direction measurement characteristic."""

    _template = ScaledUint16Template()
