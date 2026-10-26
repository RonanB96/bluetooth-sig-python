"""Advertising Constant Tone Extension Interval characteristic (0x2BB1)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class AdvertisingConstantToneExtensionIntervalCharacteristic(BaseCharacteristic[int]):
    """Advertising Constant Tone Extension Interval characteristic (0x2BB1).

    org.bluetooth.characteristic.advertising_constant_tone_extension_interval

    The interval value for Constant Tone Extension advertising.
    2-byte unsigned integer in units of 1.25 ms. Valid range: 0x0006-0xFFFF.
    """

    _template = Uint16Template()
