"""UV Index characteristic implementation."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class UVIndexCharacteristic(BaseCharacteristic):
    """UV Index characteristic (0x2A76).

    org.bluetooth.characteristic.uv_index

    UV Index characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()

    _characteristic_name: str = "UV Index"
    # YAML provides uint8 -> int, which is correct for UV Index values (0-11+ scale)
