"""Apparent Wind Speed characteristic implementation."""

from dataclasses import dataclass

from .templates import WindSpeedCharacteristic


@dataclass
class ApparentWindSpeedCharacteristic(WindSpeedCharacteristic):
    """Apparent Wind Speed measurement characteristic."""

    _characteristic_name: str = "Apparent Wind Speed"
