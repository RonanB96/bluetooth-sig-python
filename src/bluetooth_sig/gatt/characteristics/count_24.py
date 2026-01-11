"""Count 24 characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint24Template


class Count24Characteristic(BaseCharacteristic[int]):
    """Count 24 characteristic (0x2AEB).

    org.bluetooth.characteristic.count_24

    Represents a count value using 24-bit unsigned integer.
    """

    _template = Uint24Template()
