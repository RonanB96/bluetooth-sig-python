"""Track Title characteristic (0x2B97)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class TrackTitleCharacteristic(BaseCharacteristic[str]):
    """Track Title characteristic (0x2B97).

    org.bluetooth.characteristic.track_title

    Track Title characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
