"""Average Current characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageCurrentCharacteristic(BaseCharacteristic):
    """Average Current characteristic.

    Measures average electric current with 0.01 A resolution.
    """

    _template = ScaledUint16Template()

    _manual_unit: str = "A"  # Override template's "units" default
    resolution: float = 0.01
