"""Rainfall characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class RainfallCharacteristic(BaseCharacteristic):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters. Uses
    uint16 with 1 mm resolution (1:1 scaling).
    """

    _template = ScaledUint16Template(scale_factor=1.0)  # 1mm resolution

    _manual_unit: str = "mm"  # Override template's "units" default
    resolution: float = 1.0  # 1mm resolution
