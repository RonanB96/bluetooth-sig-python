"""Track Duration characteristic (0x2B98)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint32Template


class TrackDurationCharacteristic(BaseCharacteristic[int]):
    """Track Duration characteristic (0x2B98).

    org.bluetooth.characteristic.track_duration

    Duration of the current track in hundredths of a second.
    A value of -1 indicates the duration is unknown.
    """

    _template = Sint32Template()
