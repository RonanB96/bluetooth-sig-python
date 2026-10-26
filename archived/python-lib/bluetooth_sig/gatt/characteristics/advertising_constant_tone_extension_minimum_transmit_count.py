"""Advertising Constant Tone Extension Minimum Transmit Count characteristic (0x2BAF)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic(BaseCharacteristic[int]):
    """Advertising CTE Minimum Transmit Count characteristic (0x2BAF).

    org.bluetooth.characteristic.advertising_constant_tone_extension_minimum_transmit_count

    The minimum number of Constant Tone Extension transmissions.
    """

    _template = Uint8Template()
