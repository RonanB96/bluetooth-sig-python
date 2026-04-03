"""Media Player Name characteristic (0x2B93)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class MediaPlayerNameCharacteristic(BaseCharacteristic[str]):
    """Media Player Name characteristic (0x2B93).

    org.bluetooth.characteristic.media_player_name

    Media Player Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
