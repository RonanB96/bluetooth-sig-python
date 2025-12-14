"""Floor Number characteristic implementation."""

from __future__ import annotations

from ..constants import SINT8_MAX, SINT8_MIN
from .base import BaseCharacteristic
from .templates import Sint8Template


class FloorNumberCharacteristic(BaseCharacteristic):
    """Floor Number characteristic (0x2AB2).

    org.bluetooth.characteristic.floor_number

    Floor Number characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # sint8
    min_value: int = SINT8_MIN
    max_value: int = SINT8_MAX
    expected_type: type = int

    _template = Sint8Template()
