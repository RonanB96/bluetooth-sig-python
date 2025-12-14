"""Rainfall characteristic implementation."""

from __future__ import annotations

from ...types.units import LengthUnit
from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class RainfallCharacteristic(BaseCharacteristic):
    """Rainfall characteristic (0x2A78).

    org.bluetooth.characteristic.rainfall

    Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters. Uses
    uint16 with 1 mm resolution (1:1 scaling).
    """

    _template = ScaledUint16Template(scale_factor=1.0)  # 1mm resolution

    _manual_unit: str = LengthUnit.MILLIMETERS.value  # Override template's "units" default
    resolution: float = 1.0  # 1mm resolution

    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = UINT16_MAX * 1.0  # Max scaled value
    expected_type: type = float
