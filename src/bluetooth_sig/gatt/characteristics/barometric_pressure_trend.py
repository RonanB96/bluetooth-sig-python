"""Barometric Pressure Trend characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class BarometricPressureTrend(IntEnum):
    """Barometric pressure trend enumeration."""

    UNKNOWN = 0
    CONTINUOUSLY_FALLING = 1
    CONTINUOUSLY_RISING = 2
    FALLING_THEN_STEADY = 3
    RISING_THEN_STEADY = 4
    FALLING_BEFORE_LESSER_RISE = 5
    FALLING_BEFORE_GREATER_RISE = 6
    RISING_BEFORE_GREATER_FALL = 7
    RISING_BEFORE_LESSER_FALL = 8
    STEADY = 9

    def __str__(self) -> str:
        """Return human-readable description."""
        descriptions = {
            0: "Unknown",
            1: "Continuously falling",
            2: "Continuously rising",
            3: "Falling, then steady",
            4: "Rising, then steady",
            5: "Falling before a lesser rise",
            6: "Falling before a greater rise",
            7: "Rising before a greater fall",
            8: "Rising before a lesser fall",
            9: "Steady",
        }
        return descriptions[self.value]

    @classmethod
    def from_value(cls, value: int) -> BarometricPressureTrend:
        """Create enum from integer value with fallback to UNKNOWN."""
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class BarometricPressureTrendCharacteristic(BaseCharacteristic[BarometricPressureTrend]):
    """Barometric Pressure Trend characteristic (0x2AA3).

    org.bluetooth.characteristic.barometric_pressure_trend

    Barometric pressure trend characteristic.

    Represents the trend observed for barometric pressure using
    enumerated values.
    """

    _template = EnumTemplate.uint8(BarometricPressureTrend)

    # Manual override: YAML indicates uint8->int but we return enum
    _manual_value_type = "BarometricPressureTrend"
