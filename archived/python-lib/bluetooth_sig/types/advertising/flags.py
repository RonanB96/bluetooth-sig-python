"""BLE Advertising Flags (Core Spec Supplement, Part A, Section 1.3)."""

from __future__ import annotations

from enum import IntFlag


class BLEAdvertisingFlags(IntFlag):
    """BLE Advertising Flags (Core Spec Supplement, Part A, Section 1.3).

    These flags indicate the discoverable mode and capabilities of the advertising device.
    """

    LE_LIMITED_DISCOVERABLE_MODE = 0x01
    LE_GENERAL_DISCOVERABLE_MODE = 0x02
    BR_EDR_NOT_SUPPORTED = 0x04
    SIMULTANEOUS_LE_BR_EDR_CONTROLLER = 0x08
    SIMULTANEOUS_LE_BR_EDR_HOST = 0x10
    RESERVED_BIT_5 = 0x20
    RESERVED_BIT_6 = 0x40
    RESERVED_BIT_7 = 0x80
