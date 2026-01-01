"""Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class SportType(IntEnum):
    """Sport type enumeration for aerobic and anaerobic thresholds."""

    UNSPECIFIED = 0
    RUNNING_TREADMILL = 1
    CYCLING_ERGOMETER = 2
    ROWING_ERGOMETER = 3
    CROSS_TRAINING_ELLIPTICAL = 4
    CLIMBING = 5
    SKIING = 6
    SKATING = 7
    ARM_EXERCISING = 8
    LOWER_BODY_EXERCISING = 9
    UPPER_BODY_EXERCISING = 10
    WHOLE_BODY_EXERCISING = 11


class SportTypeForAerobicAndAnaerobicThresholdsCharacteristic(BaseCharacteristic):
    """Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93).

    org.bluetooth.characteristic.sport_type_for_aerobic_and_anaerobic_thresholds

    The Sport Type for Aerobic and Anaerobic Thresholds characteristic is used to represent
    the sport type applicable to aerobic and anaerobic thresholds for a user.
    """

    _template = EnumTemplate.uint8(SportType)
