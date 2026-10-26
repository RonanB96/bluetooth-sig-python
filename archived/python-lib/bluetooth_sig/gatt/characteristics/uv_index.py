"""UV Index characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class UVIndexCharacteristic(BaseCharacteristic[int]):
    """UV Index characteristic (0x2A76).

    org.bluetooth.characteristic.uv_index

    UV Index characteristic.
    """

    _template = Uint8Template()

    _characteristic_name: str = "UV Index"
    # YAML provides uint8 -> int, which is correct for UV Index values (0-11+ scale)
