"""Date UTC characteristic (0x2AED)."""

from __future__ import annotations

from datetime import date

from .base import BaseCharacteristic
from .templates import EpochDateTemplate


class DateUtcCharacteristic(BaseCharacteristic[date]):
    """Date UTC characteristic (0x2AED).

    org.bluetooth.characteristic.date_utc

    Number of days elapsed since the Epoch (Jan 1, 1970) in UTC.
    """

    _template = EpochDateTemplate()
