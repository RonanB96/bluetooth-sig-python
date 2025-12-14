"""Heat Index characteristic implementation."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class HeatIndexCharacteristic(BaseCharacteristic):
    """Heat Index characteristic (0x2A7A).

    org.bluetooth.characteristic.heat_index

    Heat Index measurement characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = UINT8_MAX
    expected_type: type = int

    _template = Uint8Template()
