"""On-demand Ranging Data characteristic (0x2C16).

Variable-length on-demand ranging measurement data.

References:
    Bluetooth SIG Ranging Service
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class OnDemandRangingDataCharacteristic(BaseCharacteristic[bytes]):
    """On-demand Ranging Data characteristic (0x2C16).

    org.bluetooth.characteristic.on_demand_ranging_data

    Contains variable-length on-demand ranging measurement data.
    """

    _manual_role = CharacteristicRole.MEASUREMENT
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
