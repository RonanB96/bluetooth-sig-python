"""ACS Data Out Indicate characteristic (0x2B32).

Indicate-only raw data output for Audio Control Service.

References:
    Bluetooth SIG Audio Control Service
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ACSDataOutIndicateCharacteristic(BaseCharacteristic[bytes]):
    """ACS Data Out Indicate characteristic (0x2B32).

    org.bluetooth.characteristic.acs_data_out_indicate

    Indicate-only raw data output for Audio Control Service.
    """

    _manual_role = CharacteristicRole.STATUS
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
