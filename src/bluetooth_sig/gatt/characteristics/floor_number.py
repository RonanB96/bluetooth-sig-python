"""Floor Number characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic

# IPS spec §3.6: encoded value X = floor_number N + 20.
_FLOOR_OFFSET = 20


class FloorNumberCharacteristic(BaseCharacteristic[int]):
    """Floor Number characteristic (0x2AB2).

    org.bluetooth.characteristic.floor_number

    IPS spec §3.6: raw uint8 X = N + 20, where N is the floor number.
    Decoded floor number = X − 20.  X = 255 means not configured.
    """

    _manual_role = CharacteristicRole.INFO

    # IPS spec §3.6: unsigned 8-bit integer, fixed 1-byte payload.
    expected_length = 1
    min_length = 1
    max_length = 1

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Decode floor number: N = raw_uint8 − 20 (IPS spec §3.6)."""
        return data[0] - _FLOOR_OFFSET

    def _encode_value(self, value: int) -> bytearray:
        """Encode floor number: raw = N + 20 (IPS spec §3.6)."""
        raw = value + _FLOOR_OFFSET
        if not 0 <= raw <= 255:
            raise ValueError(f"Floor number {value} is outside encodable range [-20, 235]")
        return bytearray([raw])
