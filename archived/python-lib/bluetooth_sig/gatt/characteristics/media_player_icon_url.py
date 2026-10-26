"""Media Player Icon URL characteristic (0x2B95)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class MediaPlayerIconURLCharacteristic(BaseCharacteristic[str]):
    """Media Player Icon URL characteristic (0x2B95).

    org.bluetooth.characteristic.media_player_icon_url

    Media Player Icon URL characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
