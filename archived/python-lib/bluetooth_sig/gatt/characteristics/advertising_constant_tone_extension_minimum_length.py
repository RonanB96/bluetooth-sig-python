"""Advertising Constant Tone Extension Minimum Length characteristic (0x2BAE)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AdvertisingConstantToneExtensionMinimumLengthCharacteristic(BaseCharacteristic[int]):
    """Advertising Constant Tone Extension Minimum Length characteristic (0x2BAE).

    org.bluetooth.characteristic.advertising_constant_tone_extension_minimum_length

    The minimum length of the Constant Tone Extension in 8 microsecond units.
    """

    _template = Uint8Template()
