"""Anaerobic Threshold characteristic (0x2A83)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicThresholdCharacteristic(BaseCharacteristic[int]):
    """Anaerobic Threshold characteristic (0x2A83).

    org.bluetooth.characteristic.anaerobic_threshold

    Anaerobic Threshold characteristic.
    """

    _template = Uint8Template()
