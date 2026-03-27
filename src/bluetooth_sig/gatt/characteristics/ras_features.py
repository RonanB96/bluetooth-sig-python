"""RAS Features characteristic (0x2C14).

Bitfield indicating the supported Ranging Service features.

References:
    Bluetooth SIG Ranging Service
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class RASFeatures(IntFlag):
    """Ranging Service feature flags (uint16)."""

    REAL_TIME_RANGING_DATA_SUPPORTED = 0x0001
    RETRIEVE_LOST_RANGING_DATA_SUPPORTED = 0x0002
    ABORT_OPERATION_SUPPORTED = 0x0004
    FILTER_RANGING_DATA_SUPPORTED = 0x0008
    RANGING_DATA_READY_SUPPORTED = 0x0010
    RANGING_DATA_OVERWRITTEN_SUPPORTED = 0x0020


class RASFeaturesCharacteristic(BaseCharacteristic[RASFeatures]):
    """RAS Features characteristic (0x2C14).

    org.bluetooth.characteristic.ras_features

    Bitfield indicating the supported Ranging Service features.
    """

    _template = FlagTemplate.uint16(RASFeatures)
