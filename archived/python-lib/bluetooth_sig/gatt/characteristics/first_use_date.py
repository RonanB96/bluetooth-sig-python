"""First Use Date characteristic (0x2C0E)."""

from __future__ import annotations

from datetime import date

from .base import BaseCharacteristic
from .templates import EpochDateTemplate


class FirstUseDateCharacteristic(BaseCharacteristic[date]):
    """First Use Date characteristic (0x2C0E).

    org.bluetooth.characteristic.first_use_date

    Number of days elapsed since the Epoch (Jan 1, 1970) representing
    the first use date.
    """

    _template = EpochDateTemplate()
