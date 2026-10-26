"""Health Sensor Features characteristic (0x2BF3)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class HealthSensorFeatures(IntFlag):
    """Health Sensor feature flags."""

    OBSERVATION_TYPE_SUPPORTED = 0x0001


class HealthSensorFeaturesCharacteristic(BaseCharacteristic[HealthSensorFeatures]):
    """Health Sensor Features characteristic (0x2BF3).

    org.bluetooth.characteristic.health_sensor_features

    Bitfield indicating the supported Health Sensor features.
    """

    _template = FlagTemplate.uint32(HealthSensorFeatures)
