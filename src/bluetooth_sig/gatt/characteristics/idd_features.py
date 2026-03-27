"""IDD Features characteristic (0x2B23).

Insulin Delivery Device supported features as a 32-bit bitfield.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class IDDFeatures(IntFlag):
    """IDD Feature flags (uint32)."""

    E2E_PROTECTION_SUPPORTED = 0x00000001
    BASAL_RATE_DELIVERY_SUPPORTED = 0x00000002
    TBR_TYPE_ABSOLUTE_SUPPORTED = 0x00000004
    TBR_TYPE_RELATIVE_SUPPORTED = 0x00000008
    TMR_DELIVERY_SUPPORTED = 0x00000010
    PROFILE_TEMPLATE_SUPPORTED = 0x00000020
    ISF_PROFILE_TEMPLATE_SUPPORTED = 0x00000040
    I2CHO_RATIO_PROFILE_TEMPLATE_SUPPORTED = 0x00000080
    TARGET_GLUCOSE_PROFILE_TEMPLATE_SUPPORTED = 0x00000100
    ISF_PROFILE_SUPPORTED = 0x00000200
    I2CHO_RATIO_PROFILE_SUPPORTED = 0x00000400
    TARGET_GLUCOSE_SUPPORTED = 0x00000800
    USER_FACING_TIME_SUPPORTED = 0x00001000
    HISTORY_EVENTS_SUPPORTED = 0x00002000


class IDDFeaturesCharacteristic(BaseCharacteristic[IDDFeatures]):
    """IDD Features characteristic (0x2B23).

    org.bluetooth.characteristic.idd_features

    Reports supported features of the Insulin Delivery Device.
    """

    _template = FlagTemplate.uint32(IDDFeatures)
