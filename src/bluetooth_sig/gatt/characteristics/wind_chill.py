"""Wind Chill characteristic implementation."""

from dataclasses import dataclass

from .templates import TemperatureLikeSint8Characteristic


@dataclass
class WindChillCharacteristic(TemperatureLikeSint8Characteristic):
    """Wind Chill measurement characteristic."""

    _characteristic_name: str = "Wind Chill"
