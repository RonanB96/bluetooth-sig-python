"""Hearing Aid Features characteristic (0x2BDA)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class HearingAidFeatures(IntFlag):
    """Hearing Aid feature flags."""

    PRESET_SYNCHRONIZATION_SUPPORT = 0x01
    INDEPENDENT_PRESETS = 0x02
    DYNAMIC_PRESETS = 0x04
    WRITABLE_PRESETS = 0x08


class HearingAidFeaturesCharacteristic(BaseCharacteristic[HearingAidFeatures]):
    """Hearing Aid Features characteristic (0x2BDA).

    org.bluetooth.characteristic.hearing_aid_features

    Bitfield indicating the supported Hearing Aid features.
    """

    _template = FlagTemplate.uint8(HearingAidFeatures)
