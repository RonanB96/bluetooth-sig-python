"""Audio Output Description characteristic (0x2B83)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class AudioOutputDescriptionCharacteristic(BaseCharacteristic[str]):
    """Audio Output Description characteristic (0x2B83).

    org.bluetooth.characteristic.audio_output_description

    Audio Output Description characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
