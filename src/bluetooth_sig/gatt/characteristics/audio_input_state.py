"""Audio Input State characteristic (0x2B77)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AudioInputMuteState(IntEnum):
    """Audio input mute state."""

    NOT_MUTED = 0
    MUTED = 1
    DISABLED = 2


class AudioInputGainMode(IntEnum):
    """Audio input gain mode."""

    MANUAL_ONLY = 0
    AUTOMATIC_ONLY = 1
    MANUAL = 2
    AUTOMATIC = 3


class AudioInputStateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Audio Input State characteristic.

    Contains gain setting, mute state, gain mode, and change counter.
    """

    gain_setting: int
    mute: AudioInputMuteState
    gain_mode: AudioInputGainMode
    change_counter: int


class AudioInputStateCharacteristic(BaseCharacteristic[AudioInputStateData]):
    """Audio Input State characteristic (0x2B77).

    org.bluetooth.characteristic.audio_input_state

    Reports the current audio input state including gain, mute,
    gain mode, and change counter.
    """

    expected_length = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AudioInputStateData:
        """Parse Audio Input State data.

        Format: gain_setting (sint8) + mute (uint8) + gain_mode (uint8) + change_counter (uint8).
        """
        gain_setting = DataParser.parse_int8(data, 0, signed=True)
        mute = AudioInputMuteState(DataParser.parse_int8(data, 1, signed=False))
        gain_mode = AudioInputGainMode(DataParser.parse_int8(data, 2, signed=False))
        change_counter = DataParser.parse_int8(data, 3, signed=False)
        return AudioInputStateData(
            gain_setting=gain_setting,
            mute=mute,
            gain_mode=gain_mode,
            change_counter=change_counter,
        )

    def _encode_value(self, data: AudioInputStateData) -> bytearray:
        """Encode Audio Input State data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.gain_setting, signed=True)
        result += DataParser.encode_int8(int(data.mute))
        result += DataParser.encode_int8(int(data.gain_mode))
        result += DataParser.encode_int8(data.change_counter)
        return result
