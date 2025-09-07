"""Barometric Pressure Trend characteristic implementation."""

from dataclasses import dataclass
from enum import IntEnum

from .base import BaseCharacteristic


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
    def from_value(cls, value: int) -> 'BarometricPressureTrend':
        """Create enum from integer value with fallback to UNKNOWN."""
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass
class BarometricPressureTrendCharacteristic(BaseCharacteristic):
    """Barometric pressure trend characteristic.

    Represents the trend observed for barometric pressure using
    enumerated values.
    """

    _characteristic_name: str = "Barometric Pressure Trend"
    # Manual override: YAML indicates uint8->int but we return descriptive strings
    _manual_value_type: str = "string"

    def parse_value(self, data: bytearray) -> str:
        """Parse barometric pressure trend data (uint8 enumerated value)."""
        if len(data) < 1:
            raise ValueError("Barometric pressure trend data must be at least 1 byte")

        trend_value = data[0]
        trend_enum = BarometricPressureTrend.from_value(trend_value)
        
        # Return human-readable description or "Reserved" for unknown values
        if trend_enum != BarometricPressureTrend.UNKNOWN and trend_value < 10:
            return str(trend_enum)
        if 10 <= trend_value <= 255:
            return f"Reserved (value: {trend_value})"
        return f"Invalid (value: {trend_value})"

    def encode_value(self, data: BarometricPressureTrend) -> bytearray:
        """Encode barometric pressure trend value back to bytes.

        Args:
            data: BarometricPressureTrend enum value

        Returns:
            Encoded bytes representing the trend (uint8 enumerated value)
        """
        if not isinstance(data, BarometricPressureTrend):
            raise TypeError(
                f"Barometric pressure trend data must be a BarometricPressureTrend enum, "
                f"got {type(data).__name__}"
            )

        return bytearray([data.value])

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for enumerated values
