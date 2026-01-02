"""Database Change Increment characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint32Template


class DatabaseChangeIncrementCharacteristic(BaseCharacteristic):
    """Database Change Increment characteristic (0x2A99).

    org.bluetooth.characteristic.database_change_increment

    Indicates database changes as an unsigned 32-bit integer.
    """

    _template = Uint32Template()
