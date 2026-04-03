"""TMAP Role characteristic (0x2B51)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class TMAPRole(IntFlag):
    """Telephony and Media Audio Profile role flags."""

    CALL_GATEWAY = 0x0001
    CALL_TERMINAL = 0x0002
    UNICAST_MEDIA_SENDER = 0x0004
    UNICAST_MEDIA_RECEIVER = 0x0008
    BROADCAST_MEDIA_SENDER = 0x0010
    BROADCAST_MEDIA_RECEIVER = 0x0020


class TMAPRoleCharacteristic(BaseCharacteristic[TMAPRole]):
    """TMAP Role characteristic (0x2B51).

    org.bluetooth.characteristic.tmap_role

    Bitfield indicating the supported Telephony and Media Audio Profile roles.
    """

    _template = FlagTemplate.uint16(TMAPRole)
