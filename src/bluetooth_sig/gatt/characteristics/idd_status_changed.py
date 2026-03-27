"""IDD Status Changed characteristic (0x2B20).

32-bit bitfield indicating which IDD status fields have changed.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class IDDStatusChangedFlags(IntFlag):
    """IDD Status Changed flags (uint32)."""

    THERAPY_CONTROL_STATE_CHANGED = 0x00000001
    OPERATIONAL_STATE_CHANGED = 0x00000002
    RESERVOIR_STATUS_CHANGED = 0x00000004
    ANNUNCIATION_STATUS_CHANGED = 0x00000008
    TOTAL_DAILY_INSULIN_STATUS_CHANGED = 0x00000010
    ACTIVE_BASAL_RATE_CHANGED = 0x00000020
    ACTIVE_TBR_CHANGED = 0x00000040
    ACTIVE_BOLUS_IDS_CHANGED = 0x00000080
    HISTORY_EVENT_RECORDED = 0x00000100


class IDDStatusChangedCharacteristic(BaseCharacteristic[IDDStatusChangedFlags]):
    """IDD Status Changed characteristic (0x2B20).

    org.bluetooth.characteristic.idd_status_changed

    Bitfield indicating which IDD status fields have changed.
    """

    _template = FlagTemplate.uint32(IDDStatusChangedFlags)
