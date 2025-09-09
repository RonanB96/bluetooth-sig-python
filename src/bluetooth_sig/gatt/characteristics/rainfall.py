"""Rainfall characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class RainfallCharacteristic(ScaledUint16Characteristic):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters.
    Uses uint16 with 1 mm resolution (1:1 scaling).
    """

    _characteristic_name: str = "Rainfall"
    resolution: float = 1.0  # 1mm resolution
    measurement_unit: str = "mm"
