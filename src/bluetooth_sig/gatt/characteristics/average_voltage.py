"""Average Voltage characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class AverageVoltageCharacteristic(ScaledUint16Characteristic):
    """Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Average Voltage"
    resolution: float = 1/64
    measurement_unit: str = "V"
