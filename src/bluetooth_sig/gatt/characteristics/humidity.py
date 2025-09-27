"""Humidity characteristic implementation."""

from dataclasses import dataclass

from ..constants import PERCENTAGE_MAX
from .templates import ScaledUint16Characteristic


@dataclass
class HumidityCharacteristic(ScaledUint16Characteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"
    _manual_value_type: str = (
        "float"  # Override YAML int type since decode_value returns float
    )

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution
    measurement_unit: str = "%"
    max_value: float = PERCENTAGE_MAX  # Humidity max 100%
