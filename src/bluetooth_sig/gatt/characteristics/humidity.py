"""Humidity characteristic implementation."""

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from ..constants import PERCENTAGE_MAX
from .templates import ScaledUint16Characteristic


@dataclass
class HumidityCharacteristic(ScaledUint16Characteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"
    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str | None = field(default="%", init=False)  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution
    max_value: float = PERCENTAGE_MAX  # Humidity max 100%
