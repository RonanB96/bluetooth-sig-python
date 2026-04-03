"""IDD Status Changed characteristic (0x2B20).

16-bit bitfield indicating which IDD status fields have changed.

References:
    Bluetooth SIG Insulin Delivery Service 1.0.1, Table 4.1
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class IDDStatusChangedFlags(IntFlag):
    """IDD Status Changed flags (uint16).

    Bits 0-7 defined, bits 8-15 RFU.
    """

    THERAPY_CONTROL_STATE_CHANGED = 0x0001
    OPERATIONAL_STATE_CHANGED = 0x0002
    RESERVOIR_STATUS_CHANGED = 0x0004
    ANNUNCIATION_STATUS_CHANGED = 0x0008
    TOTAL_DAILY_INSULIN_STATUS_CHANGED = 0x0010
    ACTIVE_BASAL_RATE_STATUS_CHANGED = 0x0020
    ACTIVE_BOLUS_STATUS_CHANGED = 0x0040
    HISTORY_EVENT_RECORDED = 0x0080


class IDDStatusChangedCharacteristic(BaseCharacteristic[IDDStatusChangedFlags]):
    """IDD Status Changed characteristic (0x2B20).

    org.bluetooth.characteristic.idd_status_changed

    Bitfield indicating which IDD status fields have changed.
    """

    _template = FlagTemplate.uint16(IDDStatusChangedFlags)
