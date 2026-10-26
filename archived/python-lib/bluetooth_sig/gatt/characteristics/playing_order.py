"""Playing Order characteristic (0x2BA1)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class PlayingOrder(IntEnum):
    """Playing order enumeration."""

    SINGLE_ONCE = 0x01
    SINGLE_REPEAT = 0x02
    IN_ORDER_ONCE = 0x03
    IN_ORDER_REPEAT = 0x04
    OLDEST_ONCE = 0x05
    OLDEST_REPEAT = 0x06
    NEWEST_ONCE = 0x07
    NEWEST_REPEAT = 0x08
    SHUFFLE_ONCE = 0x09
    SHUFFLE_REPEAT = 0x0A


class PlayingOrderCharacteristic(BaseCharacteristic[PlayingOrder]):
    """Playing Order characteristic (0x2BA1).

    org.bluetooth.characteristic.playing_order

    The current playing order of the media player.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(PlayingOrder)
