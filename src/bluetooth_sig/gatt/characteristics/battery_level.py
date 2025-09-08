"""Battery level characteristic implementation."""

from dataclasses import dataclass

from .templates import PercentageCharacteristic


@dataclass
class BatteryLevelCharacteristic(PercentageCharacteristic):
    """Battery level characteristic."""

    _characteristic_name: str = "Battery Level"
