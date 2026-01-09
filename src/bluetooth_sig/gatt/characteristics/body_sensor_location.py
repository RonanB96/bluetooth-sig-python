"""Body Sensor Location characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class BodySensorLocation(IntEnum):
    """Body sensor location enumeration (0x2A38)."""

    OTHER = 0
    CHEST = 1
    WRIST = 2
    FINGER = 3
    HAND = 4
    EAR_LOBE = 5
    FOOT = 6


class BodySensorLocationCharacteristic(BaseCharacteristic[int]):
    """Body Sensor Location characteristic (0x2A38).

    Represents the location of a sensor on the human body.
    Used primarily with heart rate and other health monitoring devices.

    Spec: Bluetooth SIG Assigned Numbers, Body Sensor Location characteristic
    """

    _template = EnumTemplate.uint8(BodySensorLocation)

    # YAML has no range constraint; enforce valid enum bounds.
    min_value: int = BodySensorLocation.OTHER  # 0
    max_value: int = BodySensorLocation.FOOT  # 6
