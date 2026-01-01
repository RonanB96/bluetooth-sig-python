"""Gender characteristic (0x2A8C)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class Gender(IntEnum):
    """Gender enumeration."""

    MALE = 0
    FEMALE = 1
    UNSPECIFIED = 2


class GenderCharacteristic(BaseCharacteristic):
    """Gender characteristic (0x2A8C).

    org.bluetooth.characteristic.gender

    The Gender characteristic is used to represent the gender of a user.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(Gender)
