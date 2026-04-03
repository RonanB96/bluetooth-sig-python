"""Audio Input Description characteristic (0x2B7C)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class AudioInputDescriptionCharacteristic(BaseCharacteristic[str]):
    """Audio Input Description characteristic (0x2B7C).

    org.bluetooth.characteristic.audio_input_description

    Audio Input Description characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
