"""Barometric Pressure Trend characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class BarometricPressureTrendCharacteristic(BaseCharacteristic):
    """Barometric pressure trend characteristic.

    Represents the trend observed for barometric pressure using
    enumerated values.
    """

    _characteristic_name: str = "Barometric Pressure Trend"

    # Trend value mappings
    TREND_VALUES = {
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

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> str:
        """Parse barometric pressure trend data (uint8 enumerated value)."""
        if len(data) < 1:
            raise ValueError("Barometric pressure trend data must be at least 1 byte")

        trend_value = data[0]

        # Return human-readable description or "Reserved" for unknown values
        if trend_value in self.TREND_VALUES:
            return self.TREND_VALUES[trend_value]
        if 10 <= trend_value <= 255:
            return f"Reserved (value: {trend_value})"
        return f"Invalid (value: {trend_value})"

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for enumerated values

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "enum"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # No state class for enumerated values
