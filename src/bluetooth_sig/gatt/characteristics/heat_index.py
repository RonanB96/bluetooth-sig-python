"""Heat Index characteristic implementation."""

from dataclasses import dataclass

from .templates import TemperatureLikeUint8Characteristic


@dataclass
class HeatIndexCharacteristic(TemperatureLikeUint8Characteristic):
    """Heat Index measurement characteristic."""

    _characteristic_name: str = "Heat Index"
