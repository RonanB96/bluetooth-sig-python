"""Elevation characteristic implementation."""

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from .templates import Sint24ScaledCharacteristic


@dataclass
class ElevationCharacteristic(Sint24ScaledCharacteristic):
    """Elevation characteristic.

    Represents the elevation relative to sea level unless otherwise
    specified in the service.
    """

    _characteristic_name: str = "Elevation"
    _manual_value_type: ValueType | str | None = "float"  # Override YAML int type since decode_value returns float
    _manual_unit: str | None = field(default="m", init=False)  # Override template's "units" default
    resolution: float = 0.01
