"""Advertising Constant Tone Extension Transmit Duration characteristic (0x2BB0)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AdvertisingConstantToneExtensionTransmitDurationCharacteristic(BaseCharacteristic[int]):
    """Advertising CTE Transmit Duration characteristic (0x2BB0).

    org.bluetooth.characteristic.advertising_constant_tone_extension_transmit_duration

    The duration of Constant Tone Extension transmission in 8 microsecond units.
    """

    _template = Uint8Template()
