"""Average Voltage characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageVoltageCharacteristic(BaseCharacteristic):
    """Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template()

    _manual_unit: str = "V"  # Override template's "units" default
    resolution: float = 1 / 64
