"""Humidity characteristic implementation."""

from ...types.gatt_enums import ValueType
from ..constants import PERCENTAGE_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _template = ScaledUint16Template()

    _characteristic_name: str = "Humidity"
    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str = "%"  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution
    max_value: float = PERCENTAGE_MAX  # Humidity max 100%
