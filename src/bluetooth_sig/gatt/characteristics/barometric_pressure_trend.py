"""Barometric Pressure Trend characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import Uint8Template


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


class BarometricPressureTrendCharacteristic(BaseCharacteristic):
    """Barometric pressure trend characteristic.

    Represents the trend observed for barometric pressure using
    enumerated values.
    """

    _template = Uint8Template()  # Used for base uint8 parsing, then converted to enum

    # Manual override: YAML indicates uint8->int but we return enum
    _manual_value_type = "BarometricPressureTrend"

    enum_class = BarometricPressureTrend

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BarometricPressureTrend:
        """Parse barometric pressure trend and return enum.

        Maps reserved value (0xFF) and invalid values to UNKNOWN.
        """
        # Use template to parse uint8
        raw_value = self._template.decode_value(data, offset=0, ctx=ctx)
        # Convert to enum with fallback
        return BarometricPressureTrend.from_value(raw_value)

    def encode_value(self, data: BarometricPressureTrend | int) -> bytearray:
        """Encode barometric pressure trend enum to bytes."""
        if isinstance(data, BarometricPressureTrend):
            value = data.value
        else:
            value = int(data)
        return self._template.encode_value(value)
