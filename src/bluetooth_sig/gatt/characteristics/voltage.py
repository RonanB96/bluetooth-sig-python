"""Voltage characteristic implementation."""

from dataclasses import dataclass, field

from ..constants import UINT16_MAX
from .templates import ScaledUint16Characteristic


@dataclass
class VoltageCharacteristic(ScaledUint16Characteristic):
    """Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Voltage"
    _manual_unit: str | None = field(default="V", init=False)  # Override template's "units" default

    # Template configuration
    resolution: float = 1 / 64  # 1/64 V resolution
    max_value: float = UINT16_MAX / 64  # ~1024 V max
