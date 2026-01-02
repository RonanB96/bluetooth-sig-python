"""Acceleration Detection Status characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class AccelerationDetectionStatus(IntEnum):
    """Acceleration detection status values."""

    NO_CHANGE = 0
    CHANGE_DETECTED = 1


class AccelerationDetectionStatusCharacteristic(BaseCharacteristic):
    """Acceleration Detection Status characteristic (0x2C0B).

    org.bluetooth.characteristic.acceleration_detection_status

    The Acceleration Detection Status characteristic represents the status of detected acceleration.
    """

    _template = EnumTemplate.uint8(AccelerationDetectionStatus)
