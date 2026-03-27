"""RC Feature characteristic (0x2B1D)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class RCFeature(IntFlag):
    """Reconnection Configuration feature flags."""

    E2E_CRC_SUPPORT = 0x0001
    RECONNECTION_TIMEOUT_SUPPORT = 0x0002


class RCFeatureCharacteristic(BaseCharacteristic[RCFeature]):
    """RC Feature characteristic (0x2B1D).

    org.bluetooth.characteristic.rc_feature

    Bitfield indicating the supported Reconnection Configuration features.
    """

    _template = FlagTemplate.uint16(RCFeature)
