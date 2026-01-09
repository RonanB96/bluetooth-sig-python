"""Time Update Control Point characteristic (0x2A16) implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class TimeUpdateControlPointCommand(IntEnum):
    """Time Update Control Point commands."""

    GET_REFERENCE_UPDATE = 0x01
    CANCEL_REFERENCE_UPDATE = 0x02


class TimeUpdateControlPointCharacteristic(BaseCharacteristic[TimeUpdateControlPointCommand]):
    """Time Update Control Point characteristic.

    Allows a client to request or cancel reference time updates.

    Value: uint8 command
    - 0x01: Get Reference Time Update
    - 0x02: Cancel Reference Time Update
    """

    _template = EnumTemplate.uint8(TimeUpdateControlPointCommand)
