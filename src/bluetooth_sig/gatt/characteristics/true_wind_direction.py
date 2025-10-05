"""True Wind Direction characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class TrueWindDirectionCharacteristic(BaseCharacteristic):
    """True Wind Direction measurement characteristic."""

    _template = ScaledUint16Template()

    _characteristic_name: str = "True Wind Direction"
