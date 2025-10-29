"""Humidity characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from ...types.units import PercentageUnit
from ..constants import PERCENTAGE_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HumidityCharacteristic(BaseCharacteristic):
    """Humidity characteristic (0x2A6F).

    org.bluetooth.characteristic.humidity

    Humidity measurement characteristic.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)

    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str | None = PercentageUnit.PERCENT.value  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution
    max_value: int | float | None = PERCENTAGE_MAX  # Humidity max 100%
