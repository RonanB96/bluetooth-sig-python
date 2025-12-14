"""Age characteristic (0x2A80)."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.templates import Uint8Template
from bluetooth_sig.gatt.constants import UINT8_MAX

from .base import BaseCharacteristic


class AgeCharacteristic(BaseCharacteristic):
    """Age characteristic (0x2A80).

    org.bluetooth.characteristic.age

    Age characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = UINT8_MAX  # 255 years
    expected_type: type = int

    _template = Uint8Template()
