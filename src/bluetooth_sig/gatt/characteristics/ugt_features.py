"""UGT Features characteristic (0x2C02)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class UGTFeatures(IntFlag):
    """Unicast Game Terminal feature flags."""

    UGT_SOURCE = 0x01
    UGT_80_KBPS_SOURCE = 0x02
    UGT_SINK = 0x04
    UGT_64_KBPS_SINK = 0x08
    UGT_MULTIPLEX = 0x10
    UGT_MULTISINK = 0x20
    UGT_MULTISOURCE = 0x40


class UGTFeaturesCharacteristic(BaseCharacteristic[UGTFeatures]):
    """UGT Features characteristic (0x2C02).

    org.bluetooth.characteristic.ugt_features

    Bitfield indicating the supported Unicast Game Terminal features.
    """

    _template = FlagTemplate.uint8(UGTFeatures)
