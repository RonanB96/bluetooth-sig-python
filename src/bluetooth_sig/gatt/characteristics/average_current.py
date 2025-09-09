"""Average Current characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class AverageCurrentCharacteristic(ScaledUint16Characteristic):
    """Average Current characteristic.

    Measures average electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Average Current"
    resolution: float = 0.01
    measurement_unit: str = "A"
