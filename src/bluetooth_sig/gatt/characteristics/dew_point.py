"""Dew Point characteristic implementation."""

from dataclasses import dataclass

from .templates import TemperatureLikeSint8Characteristic


@dataclass
class DewPointCharacteristic(TemperatureLikeSint8Characteristic):
    """Dew Point measurement characteristic."""

    _characteristic_name: str = "Dew Point"
