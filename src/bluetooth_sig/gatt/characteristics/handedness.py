"""Handedness characteristic (0x2B4A)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class Handedness(IntEnum):
    """Handedness enumeration."""

    LEFT_HANDED = 0x00
    RIGHT_HANDED = 0x01
    AMBIDEXTROUS = 0x02
    UNSPECIFIED = 0x03


class HandednessCharacteristic(BaseCharacteristic[int]):
    """Handedness characteristic (0x2B4A).

    org.bluetooth.characteristic.handedness

    The Handedness characteristic is used to represent the handedness of a user.
    """

    expected_length: int | None = 1
    _template = EnumTemplate.uint8(Handedness)
