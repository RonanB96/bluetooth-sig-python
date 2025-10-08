"""Humidity characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from ..constants import PERCENTAGE_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _template = ScaledUint16Template()

    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str | None = "%"  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution
    max_value: int | float | None = PERCENTAGE_MAX  # Humidity max 100%
