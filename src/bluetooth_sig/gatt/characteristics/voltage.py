"""Voltage characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VoltageCharacteristic(BaseCharacteristic[float]):
    """Voltage characteristic (0x2B18).

    org.bluetooth.characteristic.voltage

    Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template(scale_factor=1 / 64, offset=0)

    _manual_unit: str = ElectricalUnit.VOLTS.value  # Override template's "units" default

    # Template configuration
    resolution: float = 1 / 64  # 1/64 V resolution
