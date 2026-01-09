"""Count 16 characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class Count16Characteristic(BaseCharacteristic[int]):
    """Count 16 characteristic (0x2AEA).

    org.bluetooth.characteristic.count_16

    Represents a count value using 16-bit unsigned integer.
    """

    _template = Uint16Template()
