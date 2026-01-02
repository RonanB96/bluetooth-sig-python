"""Heart Rate Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class HeartRateControlCommand(IntEnum):
    """Heart Rate Control Point command values."""

    RESERVED = 0x00
    RESET_ENERGY_EXPENDED = 0x01


class HeartRateControlPointCharacteristic(BaseCharacteristic):
    """Heart Rate Control Point characteristic (0x2A39).

    org.bluetooth.characteristic.heart_rate_control_point

    Control point for Heart Rate Service operations (e.g., reset energy expended).
    """

    _template = EnumTemplate.uint8(HeartRateControlCommand)
