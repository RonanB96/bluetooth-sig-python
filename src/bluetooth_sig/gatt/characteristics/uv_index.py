"""UV Index characteristic implementation."""

from .base import BaseCharacteristic
from .templates import Uint8Template


class UVIndexCharacteristic(BaseCharacteristic):
    """UV Index characteristic."""

    _template = Uint8Template()

    _characteristic_name: str = "UV Index"
    # YAML provides uint8 -> int, which is correct for UV Index values (0-11+ scale)
