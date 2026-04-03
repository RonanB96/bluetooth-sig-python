"""UGG Features characteristic (0x2C01)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class UGGFeatures(IntFlag):
    """Unicast Game Gateway feature flags."""

    UGG_MULTIPLEX = 0x01
    UGG_96_KBPS = 0x02
    UGG_MULTISINK = 0x04


class UGGFeaturesCharacteristic(BaseCharacteristic[UGGFeatures]):
    """UGG Features characteristic (0x2C01).

    org.bluetooth.characteristic.ugg_features

    Bitfield indicating the supported Unicast Game Gateway features.
    """

    _template = FlagTemplate.uint8(UGGFeatures)
