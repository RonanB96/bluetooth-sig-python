"""Media Player Icon Object ID characteristic (0x2B94)."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..constants import UINT48_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class MediaPlayerIconObjectIdCharacteristic(BaseCharacteristic[int]):
    """Media Player Icon Object ID characteristic (0x2B94).

    org.bluetooth.characteristic.media_player_icon_object_id

    OTS object ID for the media player icon.
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 6
    min_length: int = 6
    min_value = 0
    max_value = UINT48_MAX

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Parse media player icon object ID (uint48)."""
        return DataParser.parse_int48(data, 0, signed=False)

    def _encode_value(self, data: int) -> bytearray:
        """Encode media player icon object ID to bytes."""
        return DataParser.encode_int48(data, signed=False)
