"""BGR Features characteristic (0x2C04)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class BGRFeatures(IntFlag):
    """Broadcast Game Receiver feature flags."""

    MULTISINK = 0x01
    MULTIPLEX = 0x02


class BGRFeaturesCharacteristic(BaseCharacteristic[BGRFeatures]):
    """BGR Features characteristic (0x2C04).

    org.bluetooth.characteristic.bgr_features

    Bitfield indicating the supported Broadcast Game Receiver features.
    """

    _template = FlagTemplate.uint8(BGRFeatures)
