"""Temperature characteristic implementation."""

from dataclasses import dataclass

from .templates import TemperatureCharacteristic as TemperatureTemplate


@dataclass
class TemperatureCharacteristic(TemperatureTemplate):
    """Temperature measurement characteristic."""

    _characteristic_name: str = "Temperature"
