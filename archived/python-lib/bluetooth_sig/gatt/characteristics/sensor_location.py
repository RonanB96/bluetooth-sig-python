"""Sensor Location characteristic (0x2A5D)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class SensorLocationValue(IntEnum):
    """Sensor body location values.

    Values:
        OTHER: Other location (0)
        TOP_OF_SHOE: Top of shoe (1)
        IN_SHOE: In shoe (2)
        HIP: Hip (3)
        FRONT_WHEEL: Front wheel (4)
        LEFT_CRANK: Left crank (5)
        RIGHT_CRANK: Right crank (6)
        LEFT_PEDAL: Left pedal (7)
        RIGHT_PEDAL: Right pedal (8)
        FRONT_HUB: Front hub (9)
        REAR_DROPOUT: Rear dropout (10)
        CHAINSTAY: Chainstay (11)
        REAR_WHEEL: Rear wheel (12)
        REAR_HUB: Rear hub (13)
        CHEST: Chest (14)
        SPIDER: Spider (15)
        CHAIN_RING: Chain ring (16)
    """

    OTHER = 0
    TOP_OF_SHOE = 1
    IN_SHOE = 2
    HIP = 3
    FRONT_WHEEL = 4
    LEFT_CRANK = 5
    RIGHT_CRANK = 6
    LEFT_PEDAL = 7
    RIGHT_PEDAL = 8
    FRONT_HUB = 9
    REAR_DROPOUT = 10
    CHAINSTAY = 11
    REAR_WHEEL = 12
    REAR_HUB = 13
    CHEST = 14
    SPIDER = 15
    CHAIN_RING = 16


class SensorLocationCharacteristic(BaseCharacteristic[SensorLocationValue]):
    """Sensor Location characteristic (0x2A5D).

    org.bluetooth.characteristic.sensor_location

    Body location of a sensor (17 named positions).
    Values 17-255 are reserved for future use.
    """

    _template = EnumTemplate.uint8(SensorLocationValue)
