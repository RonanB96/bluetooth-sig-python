"""Device Time Feature characteristic (0x2B8E).

Per DTS v1.0 Table 3.2, the characteristic contains:
  E2E_CRC (uint16, conditional) + DT_Features (uint16, mandatory).

The DT_Features field is 2 octets (uint16).  Bits 0-12 are defined in
Table 3.3.  Bits 13-15 are Reserved for Future Use.

References:
    Bluetooth SIG Device Time Service v1.0, Table 3.2, Table 3.3
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class DeviceTimeFeatureFlags(IntFlag):
    """DT_Features bitfield — DTS v1.0 Table 3.3.

    Each bit indicates whether the corresponding service feature is supported.
    Bits 13-15 are Reserved for Future Use.
    """

    E2E_CRC = 0x0001  # Bit 0
    TIME_CHANGE_LOGGING = 0x0002  # Bit 1
    BASE_TIME_SECOND_FRACTIONS = 0x0004  # Bit 2
    TIME_OR_DATE_DISPLAYED_TO_USER = 0x0008  # Bit 3
    DISPLAYED_FORMATS = 0x0010  # Bit 4
    DISPLAYED_FORMATS_CHANGEABLE = 0x0020  # Bit 5
    SEPARATE_USER_TIMELINE = 0x0040  # Bit 6
    AUTHORIZATION_REQUIRED = 0x0080  # Bit 7
    RTC_DRIFT_TRACKING = 0x0100  # Bit 8
    EPOCH_YEAR_1900 = 0x0200  # Bit 9
    EPOCH_YEAR_2000 = 0x0400  # Bit 10
    PROPOSE_NON_LOGGED_TIME_ADJUSTMENT_LIMIT = 0x0800  # Bit 11
    RETRIEVE_ACTIVE_TIME_ADJUSTMENTS = 0x1000  # Bit 12


class DeviceTimeFeatureCharacteristic(BaseCharacteristic[DeviceTimeFeatureFlags]):
    """Device Time Feature characteristic (0x2B8E).

    org.bluetooth.characteristic.device_time_feature

    Describes the features supported by the Device Time Service.
    The DT_Features field is 2 octets (uint16).  When the E2E-CRC feature
    is not supported, the characteristic contains only DT_Features (2 octets).
    """

    expected_length: int = 2
    _template = FlagTemplate.uint16(DeviceTimeFeatureFlags)
