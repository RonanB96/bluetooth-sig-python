"""Aerobic Threshold characteristic (0x2A7E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AerobicThresholdCharacteristic(BaseCharacteristic):
    """Aerobic Threshold characteristic (0x2A7E).

    org.bluetooth.characteristic.aerobic_threshold

    Aerobic Threshold characteristic.
    """

    _template = Uint8Template()
