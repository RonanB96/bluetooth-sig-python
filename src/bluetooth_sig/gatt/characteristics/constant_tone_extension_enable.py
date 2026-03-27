"""Constant Tone Extension Enable characteristic."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class CTEEnableState(IntEnum):
    """Constant Tone Extension enable state."""

    DISABLED = 0
    ENABLED = 1


class ConstantToneExtensionEnableCharacteristic(BaseCharacteristic[CTEEnableState]):
    """Constant Tone Extension Enable characteristic (0x2BAD).

    org.bluetooth.characteristic.constant_tone_extension_enable

    Indicates whether the Constant Tone Extension is enabled (1) or disabled (0).
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(CTEEnableState)
