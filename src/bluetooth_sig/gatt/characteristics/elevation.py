"""Elevation characteristic implementation."""

from dataclasses import dataclass

from .templates import Sint24ScaledCharacteristic


@dataclass
class ElevationCharacteristic(Sint24ScaledCharacteristic):
    """Elevation characteristic.

    Represents the elevation relative to sea level unless otherwise
    specified in the service.
    """

    _characteristic_name: str = "Elevation"
    _manual_value_type: str = (
        "float"  # Override YAML int type since decode_value returns float
    )
    resolution: float = 0.01
    measurement_unit: str = "m"
