"""Audio Input Type characteristic (0x2B79)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class AudioInputType(IntEnum):
    """Audio input type."""

    UNSPECIFIED = 0x00
    BLUETOOTH = 0x01
    MICROPHONE = 0x02
    ANALOG = 0x03
    DIGITAL = 0x04
    RADIO = 0x05
    STREAMING = 0x06
    AMBIENT = 0x07


class AudioInputTypeCharacteristic(BaseCharacteristic[AudioInputType]):
    """Audio Input Type characteristic (0x2B79).

    org.bluetooth.characteristic.audio_input_type

    Type of audio input.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(AudioInputType)
