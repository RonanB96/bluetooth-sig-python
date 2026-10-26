"""Set Member Lock characteristic (0x2B86)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class SetMemberLockState(IntEnum):
    """Set member lock state."""

    UNLOCKED = 0x01
    LOCKED = 0x02


class SetMemberLockCharacteristic(BaseCharacteristic[SetMemberLockState]):
    """Set Member Lock characteristic (0x2B86).

    org.bluetooth.characteristic.lock_characteristic

    The lock state of a coordinated set member.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(SetMemberLockState)
