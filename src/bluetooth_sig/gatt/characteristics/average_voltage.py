"""Average Voltage characteristic implementation."""

from dataclasses import dataclass, field

from .templates import ScaledUint16Characteristic


@dataclass
class AverageVoltageCharacteristic(ScaledUint16Characteristic):
    """Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Average Voltage"
    _manual_unit: str | None = field(default="V", init=False)  # Override template's "units" default
    resolution: float = 1 / 64
