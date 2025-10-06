"""Voltage characteristic implementation."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VoltageCharacteristic(BaseCharacteristic):
    """Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template()

    _characteristic_name: str = "Voltage"
    _manual_unit: str = "V"  # Override template's "units" default

    # Template configuration
    resolution: float = 1 / 64  # 1/64 V resolution
    max_value: float = UINT16_MAX / 64  # ~1024 V max
