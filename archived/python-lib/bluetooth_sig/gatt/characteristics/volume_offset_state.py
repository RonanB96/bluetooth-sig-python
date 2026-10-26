"""Volume Offset State characteristic (0x2B80)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VolumeOffsetStateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Volume Offset State characteristic.

    Contains the volume offset and change counter.
    """

    volume_offset: int
    change_counter: int


class VolumeOffsetStateCharacteristic(BaseCharacteristic[VolumeOffsetStateData]):
    """Volume Offset State characteristic (0x2B80).

    org.bluetooth.characteristic.volume_offset_state

    Reports the current volume offset and change counter
    for the Volume Offset Control Service.
    """

    expected_length = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VolumeOffsetStateData:
        """Parse Volume Offset State data.

        Format: volume_offset (sint16 LE) + change_counter (uint8).
        """
        volume_offset = DataParser.parse_int16(data, 0, signed=True)
        change_counter = DataParser.parse_int8(data, 2, signed=False)
        return VolumeOffsetStateData(
            volume_offset=volume_offset,
            change_counter=change_counter,
        )

    def _encode_value(self, data: VolumeOffsetStateData) -> bytearray:
        """Encode Volume Offset State data to bytes."""
        result = bytearray()
        result += DataParser.encode_int16(data.volume_offset, signed=True)
        result += DataParser.encode_int8(data.change_counter)
        return result
