"""Device Time Feature characteristic (0x2B8E)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class DeviceTimeFeatureFlags(IntFlag):
    """Device Time Feature flags."""

    DEVICE_TIME_SET = 0x01
    TIME_CHANGE_LOGGING = 0x02
    DEVICE_TIME_PERSISTENCE = 0x04
    REFERENCE_TIME_INFORMATION = 0x08


class DeviceTimeFeatureCharacteristic(BaseCharacteristic[DeviceTimeFeatureFlags]):
    """Device Time Feature characteristic (0x2B8E).

    org.bluetooth.characteristic.device_time_feature

    Describes the features supported by the Device Time service.
    """

    expected_length: int = 1
    _template = FlagTemplate.uint8(DeviceTimeFeatureFlags)
