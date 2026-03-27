"""Advertising Constant Tone Extension Interval characteristic (0x2BB1)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AdvertisingConstantToneExtensionIntervalCharacteristic(BaseCharacteristic[int]):
    """Advertising Constant Tone Extension Interval characteristic (0x2BB1).

    org.bluetooth.characteristic.advertising_constant_tone_extension_interval

    The interval value for Constant Tone Extension advertising.
    """

    _template = Uint8Template()
