"""BGS Features characteristic (0x2C03)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class BGSFeatures(IntFlag):
    """Broadcast Game Sender feature flags."""

    MULTISINK = 0x01
    MULTIPLEX = 0x02


class BGSFeaturesCharacteristic(BaseCharacteristic[BGSFeatures]):
    """BGS Features characteristic (0x2C03).

    org.bluetooth.characteristic.bgs_features

    Bitfield indicating the supported Broadcast Game Sender features.
    """

    _template = FlagTemplate.uint8(BGSFeatures)
