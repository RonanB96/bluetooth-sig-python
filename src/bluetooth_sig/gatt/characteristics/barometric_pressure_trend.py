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
    # Manual override: YAML indicates uint8->int but we return descriptive strings
    _manual_value_type: str = "string"

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

    def encode_value(self, data: str | int) -> bytearray:
        """Encode barometric pressure trend value back to bytes.

        Args:
            data: Pressure trend either as string description or as raw uint8 value

        Returns:
            Encoded bytes representing the trend (uint8 enumerated value)
        """
        if isinstance(data, int):
            # Direct raw value
            trend_value = data
        elif isinstance(data, str):
            # Map string description back to numeric value
            reverse_map = {v: k for k, v in self.TREND_VALUES.items()}
            if data in reverse_map:
                trend_value = reverse_map[data]
            elif data.startswith("Reserved (value: "):
                # Parse reserved value format
                try:
                    trend_value = int(data.split("value: ")[1].rstrip(")"))
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid reserved trend format: {data}") from e
            elif data.startswith("Invalid (value: "):
                # Parse invalid value format
                try:
                    trend_value = int(data.split("value: ")[1].rstrip(")"))
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid trend format: {data}") from e
            else:
                raise ValueError(f"Unknown barometric pressure trend: {data}")
        else:
            raise TypeError(
                "Barometric pressure trend data must be a string or integer"
            )

        # Validate range for uint8 (0 to 255)
        if not 0 <= trend_value <= 255:
            raise ValueError(
                f"Trend value {trend_value} is outside valid range (0-255)"
            )

        return bytearray([trend_value])

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # No unit for enumerated values
