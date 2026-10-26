"""GMAP Role characteristic (0x2C00)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class GMAPRole(IntFlag):
    """Gaming Audio Profile role flags."""

    UNICAST_GAME_GATEWAY = 0x01
    UNICAST_GAME_TERMINAL = 0x02
    BROADCAST_GAME_SENDER = 0x04
    BROADCAST_GAME_RECEIVER = 0x08


class GMAPRoleCharacteristic(BaseCharacteristic[GMAPRole]):
    """GMAP Role characteristic (0x2C00).

    org.bluetooth.characteristic.gmap_role

    Bitfield indicating the supported Gaming Audio Profile roles.
    """

    _template = FlagTemplate.uint8(GMAPRole)
