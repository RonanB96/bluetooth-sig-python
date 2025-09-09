"""High Voltage characteristic implementation."""

from dataclasses import dataclass

from .templates import Uint24ScaledCharacteristic


@dataclass
class HighVoltageCharacteristic(Uint24ScaledCharacteristic):
    """High Voltage characteristic.

    Measures high voltage systems using uint24 format.
    """

    _characteristic_name: str = "High Voltage"
    resolution: float = 1.0
    measurement_unit: str = "V"
