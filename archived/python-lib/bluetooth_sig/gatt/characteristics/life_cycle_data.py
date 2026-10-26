"""Life Cycle Data characteristic (0x2C0F).

Variable-length lifecycle data record from an Industrial Monitoring Device.

References:
    Bluetooth SIG Industrial Monitoring Device Service
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class LifeCycleDataCharacteristic(BaseCharacteristic[bytes]):
    """Life Cycle Data characteristic (0x2C0F).

    org.bluetooth.characteristic.life_cycle_data

    Contains variable-length lifecycle data from an Industrial Monitoring Device.
    """

    _manual_role = CharacteristicRole.INFO
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
