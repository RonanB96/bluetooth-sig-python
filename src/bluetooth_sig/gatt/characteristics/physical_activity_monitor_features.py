"""Physical Activity Monitor Features characteristic (0x2B3C).

32-bit bitfield of supported Physical Activity Monitor features.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class PhysicalActivityMonitorFeatures(IntFlag):
    """Physical Activity Monitor feature flags (uint32)."""

    GENERAL_ACTIVITY_INSTANTANEOUS_DATA_SUPPORTED = 0x00000001
    GENERAL_ACTIVITY_SUMMARY_DATA_SUPPORTED = 0x00000002
    GENERAL_ACTIVITY_STEPS_SUPPORTED = 0x00000004
    GENERAL_ACTIVITY_STEPS_COUNTER_SUPPORTED = 0x00000008
    GENERAL_ACTIVITY_DISTANCE_SUPPORTED = 0x00000010
    GENERAL_ACTIVITY_DISTANCE_IN_METRES_SUPPORTED = 0x00000020
    GENERAL_ACTIVITY_DURATION_SUPPORTED = 0x00000040
    GENERAL_ACTIVITY_INTENSITY_SUPPORTED = 0x00000080
    CARDIO_RESPIRATORY_ACTIVITY_INSTANTANEOUS_DATA_SUPPORTED = 0x00000100
    CARDIO_RESPIRATORY_ACTIVITY_SUMMARY_DATA_SUPPORTED = 0x00000200
    STEP_COUNTER_ACTIVITY_SUMMARY_DATA_SUPPORTED = 0x00000400
    SLEEP_ACTIVITY_INSTANTANEOUS_DATA_SUPPORTED = 0x00000800
    SLEEP_ACTIVITY_SUMMARY_DATA_SUPPORTED = 0x00001000
    ACTIVITY_RECOGNITION_SUPPORTED = 0x00002000
    MULTIPLE_SESSIONS_SUPPORTED = 0x00004000
    SESSION_DESCRIPTORS_SUPPORTED = 0x00008000


class PhysicalActivityMonitorFeaturesCharacteristic(BaseCharacteristic[PhysicalActivityMonitorFeatures]):
    """Physical Activity Monitor Features characteristic (0x2B3C).

    org.bluetooth.characteristic.physical_activity_monitor_features

    Reports supported features of the Physical Activity Monitor.
    """

    _template = FlagTemplate.uint32(PhysicalActivityMonitorFeatures)
