"""True Wind Direction characteristic implementation."""

from dataclasses import dataclass

from .templates import WindDirectionCharacteristic


@dataclass
class TrueWindDirectionCharacteristic(WindDirectionCharacteristic):
    """True Wind Direction measurement characteristic."""

    _characteristic_name: str = "True Wind Direction"
