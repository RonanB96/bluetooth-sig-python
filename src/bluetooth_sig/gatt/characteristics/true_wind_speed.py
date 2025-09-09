"""True Wind Speed characteristic implementation."""

from dataclasses import dataclass

from .templates import WindSpeedCharacteristic


@dataclass
class TrueWindSpeedCharacteristic(WindSpeedCharacteristic):
    """True Wind Speed measurement characteristic."""

    _characteristic_name: str = "True Wind Speed"
