"""IMD Historical Data characteristic (0x2C13).

Variable-length historical data record from an Industrial Monitoring Device.

References:
    Bluetooth SIG Industrial Monitoring Device Service
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class IMDHistoricalDataCharacteristic(BaseCharacteristic[bytes]):
    """IMD Historical Data characteristic (0x2C13).

    org.bluetooth.characteristic.imd_historical_data

    Contains variable-length historical data from an Industrial Monitoring Device.
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
