"""Volume State characteristic (0x2B7D)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VolumeMuteState(IntEnum):
    """Volume mute state."""

    NOT_MUTED = 0
    MUTED = 1


class VolumeStateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Volume State characteristic.

    Contains the current volume setting, mute state, and change counter.
    """

    volume_setting: int
    mute: VolumeMuteState
    change_counter: int


class VolumeStateCharacteristic(BaseCharacteristic[VolumeStateData]):
    """Volume State characteristic (0x2B7D).

    org.bluetooth.characteristic.volume_state

    Reports the current volume setting, mute state, and change counter
    for the Volume Control Service.
    """

    expected_length = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VolumeStateData:
        """Parse Volume State data.

        Format: volume_setting (uint8) + mute (uint8) + change_counter (uint8).
        """
        volume_setting = DataParser.parse_int8(data, 0, signed=False)
        mute = VolumeMuteState(DataParser.parse_int8(data, 1, signed=False))
        change_counter = DataParser.parse_int8(data, 2, signed=False)
        return VolumeStateData(
            volume_setting=volume_setting,
            mute=mute,
            change_counter=change_counter,
        )

    def _encode_value(self, data: VolumeStateData) -> bytearray:
        """Encode Volume State data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.volume_setting)
        result += DataParser.encode_int8(int(data.mute))
        result += DataParser.encode_int8(data.change_counter)
        return result
