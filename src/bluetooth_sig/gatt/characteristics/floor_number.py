"""Floor Number characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class FloorNumberCharacteristic(BaseCharacteristic):
    """Floor Number characteristic (0x2AB2).

    org.bluetooth.characteristic.floor_number

    Floor Number characteristic.
    """

    _template = Sint8Template()
