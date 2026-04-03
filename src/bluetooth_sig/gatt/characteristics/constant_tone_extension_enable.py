"""Constant Tone Extension Enable characteristic."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class CTEEnableFlags(IntFlag):
    """Constant Tone Extension enable flags (bitfield).

    Bit 0: Enable AoA CTE on ACL connection.
    Bit 1: Enable AoD CTE in advertising packets.
    """

    AOA_ACL = 0x01
    AOD_ADVERTISING = 0x02


class ConstantToneExtensionEnableCharacteristic(BaseCharacteristic[CTEEnableFlags]):
    """Constant Tone Extension Enable characteristic (0x2BAD).

    org.bluetooth.characteristic.constant_tone_extension_enable

    1-byte bitfield controlling CTE transmission.
    Bit 0: AoA CTE on ACL connection. Bit 1: AoD CTE in advertising.
    """

    _template = FlagTemplate.uint8(CTEEnableFlags)
