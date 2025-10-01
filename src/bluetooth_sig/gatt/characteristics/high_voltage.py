"""High Voltage characteristic implementation."""

from dataclasses import dataclass, field

from .templates import Uint24ScaledCharacteristic


@dataclass
class HighVoltageCharacteristic(Uint24ScaledCharacteristic):
    """High Voltage characteristic.

    Measures high voltage systems using uint24 format.
    """

    _characteristic_name: str = "High Voltage"
    _manual_unit: str | None = field(default="V", init=False)  # Override template's "units" default
    resolution: float = 1.0
