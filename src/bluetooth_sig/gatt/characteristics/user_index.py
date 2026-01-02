"""User Index characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class UserIndexCharacteristic(BaseCharacteristic):
    """User Index characteristic (0x2A9A).

    org.bluetooth.characteristic.user_index

    Identifies a user by index as an unsigned 8-bit integer.
    """

    _template = Uint8Template()
