"""Audio Input Status characteristic (0x2B7A)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class AudioInputStatus(IntEnum):
    """Audio input status."""

    INACTIVE = 0x00
    ACTIVE = 0x01


class AudioInputStatusCharacteristic(BaseCharacteristic[AudioInputStatus]):
    """Audio Input Status characteristic (0x2B7A).

    org.bluetooth.characteristic.audio_input_status

    Status of the audio input.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(AudioInputStatus)
