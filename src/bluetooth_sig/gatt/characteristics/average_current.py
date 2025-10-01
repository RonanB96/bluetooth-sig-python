"""Average Current characteristic implementation."""

from dataclasses import dataclass, field

from .templates import ScaledUint16Characteristic


@dataclass
class AverageCurrentCharacteristic(ScaledUint16Characteristic):
    """Average Current characteristic.

    Measures average electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Average Current"
    _manual_unit: str | None = field(default="A", init=False)  # Override template's "units" default
    resolution: float = 0.01
