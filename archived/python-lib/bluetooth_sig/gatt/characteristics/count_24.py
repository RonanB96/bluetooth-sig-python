"""Count 24 characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint24Template


class Count24Characteristic(BaseCharacteristic[int]):
    """Count 24 characteristic (0x2AEB).

    org.bluetooth.characteristic.count_24

    Represents a count value using 24-bit unsigned integer.
    """

    _manual_role = CharacteristicRole.MEASUREMENT
    _template = Uint24Template()
