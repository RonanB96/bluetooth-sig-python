"""Volume Flags characteristic (0x2B7F)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class VolumeFlags(IntFlag):
    """Volume flags."""

    RESET_VOLUME_SETTING = 0x00
    USER_SET_VOLUME_SETTING = 0x01


class VolumeFlagsCharacteristic(BaseCharacteristic[VolumeFlags]):
    """Volume Flags characteristic (0x2B7F).

    org.bluetooth.characteristic.volume_flags

    Bitfield indicating volume-related flags.
    """

    _template = FlagTemplate.uint8(VolumeFlags)
