"""Playing Orders Supported characteristic (0x2BA2)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class PlayingOrdersSupported(IntFlag):
    """Supported playing orders flags."""

    SINGLE_ONCE = 0x0001
    SINGLE_REPEAT = 0x0002
    IN_ORDER_ONCE = 0x0004
    IN_ORDER_REPEAT = 0x0008
    OLDEST_ONCE = 0x0010
    OLDEST_REPEAT = 0x0020
    NEWEST_ONCE = 0x0040
    NEWEST_REPEAT = 0x0080
    SHUFFLE_ONCE = 0x0100
    SHUFFLE_REPEAT = 0x0200


class PlayingOrdersSupportedCharacteristic(BaseCharacteristic[PlayingOrdersSupported]):
    """Playing Orders Supported characteristic (0x2BA2).

    org.bluetooth.characteristic.playing_orders_supported

    Bitfield indicating which playing orders are supported.
    """

    _template = FlagTemplate.uint16(PlayingOrdersSupported)
