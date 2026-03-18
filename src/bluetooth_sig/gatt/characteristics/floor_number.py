"""Floor Number characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Sint8Template


class FloorNumberCharacteristic(BaseCharacteristic[int]):
    """Floor Number characteristic (0x2AB2).

    org.bluetooth.characteristic.floor_number

    Floor Number characteristic.
    """

    _manual_role = CharacteristicRole.INFO

    # SIG spec: sint8 floor index → fixed 1-byte payload; no GSS YAML
    expected_length = 1
    min_length = 1
    max_length = 1
    _template = Sint8Template()
