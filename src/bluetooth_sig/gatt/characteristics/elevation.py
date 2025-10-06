"""Elevation characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ScaledSint24Template


class ElevationCharacteristic(BaseCharacteristic):
    """Elevation characteristic.

    Represents the elevation relative to sea level unless otherwise
    specified in the service.

    Format: sint24 (3 bytes) with 0.01 meter resolution.
    """

    _template = ScaledSint24Template(scale_factor=0.01)

    _manual_value_type: ValueType | str | None = "float"  # Override YAML int type since decode_value returns float
    _manual_unit: str | None = "m"  # Override template's "units" default
    resolution: float = 0.01
