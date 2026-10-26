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
    """Ranging Service feature flags (uint32, per RAS v1.0 Table 3.3)."""

    REAL_TIME_RANGING_DATA_SUPPORTED = 0x00000001
    RETRIEVE_LOST_RANGING_DATA_SEGMENTS_SUPPORTED = 0x00000002
    ABORT_OPERATION_SUPPORTED = 0x00000004
    FILTER_RANGING_DATA_SUPPORTED = 0x00000008


class RASFeaturesCharacteristic(BaseCharacteristic[RASFeatures]):
    """RAS Features characteristic (0x2C14).

    org.bluetooth.characteristic.ras_features

    Bitfield indicating the supported Ranging Service features.
    Per RAS v1.0 Table 3.2: Boolean[32] = uint32 (4 bytes).
    """

    _template = FlagTemplate.uint32(RASFeatures)
