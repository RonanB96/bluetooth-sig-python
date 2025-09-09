"""Apparent Wind Direction characteristic implementation."""

from dataclasses import dataclass

from .templates import WindDirectionCharacteristic


@dataclass
class ApparentWindDirectionCharacteristic(WindDirectionCharacteristic):
    """Apparent Wind Direction measurement characteristic."""

    _characteristic_name: str = "Apparent Wind Direction"
