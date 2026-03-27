"""ACS Data In characteristic (0x2B30).

Write-only raw data input for Audio Control Service.

References:
    Bluetooth SIG Audio Control Service
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ACSDataInCharacteristic(BaseCharacteristic[bytes]):
    """ACS Data In characteristic (0x2B30).

    org.bluetooth.characteristic.acs_data_in

    Write-only raw data input for Audio Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
