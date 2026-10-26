"""Track Position characteristic (0x2B99)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint32Template


class TrackPositionCharacteristic(BaseCharacteristic[int]):
    """Track Position characteristic (0x2B99).

    org.bluetooth.characteristic.track_position

    Position within the current track in hundredths of a second.
    A value of -1 indicates the position is unavailable.
    """

    _template = Sint32Template()
