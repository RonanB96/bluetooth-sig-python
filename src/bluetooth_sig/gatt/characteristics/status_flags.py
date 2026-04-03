"""Status Flags characteristic (0x2BBB)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class StatusFlags(IntFlag):
    """Telephone Bearer status flags."""

    INBAND_RINGTONE = 0x0001
    SILENT_MODE = 0x0002


class StatusFlagsCharacteristic(BaseCharacteristic[StatusFlags]):
    """Status Flags characteristic (0x2BBB).

    org.bluetooth.characteristic.status_flags

    Bitfield indicating the current status flags of a Telephone Bearer.
    """

    _template = FlagTemplate.uint16(StatusFlags)
