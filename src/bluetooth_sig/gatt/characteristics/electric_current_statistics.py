"""Electric Current Statistics characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic):
    """Electric Current Statistics characteristic.

    Provides statistical current data (min, max, average over time).
    """

    _characteristic_name: str = "Electric Current Statistics"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse current statistics data (3x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum', 'maximum', and 'average' current values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError(
                "Electric current statistics data must be at least 6 bytes"
            )

        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_current_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return {
            "minimum": min_current_raw * 0.01,
            "maximum": max_current_raw * 0.01,
            "average": avg_current_raw * 0.01,
        }

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode electric current statistics value back to bytes.

        Args:
            data: Dictionary with 'minimum', 'maximum', and 'average' current values in Amperes

        Returns:
            Encoded bytes representing the current statistics (3x uint16, 0.01 A resolution)
        """
        if not isinstance(data, dict):
            raise TypeError("Electric current statistics data must be a dictionary")
        
        if "minimum" not in data or "maximum" not in data or "average" not in data:
            raise ValueError("Electric current statistics data must contain 'minimum', 'maximum', and 'average' keys")
        
        min_current = float(data["minimum"])
        max_current = float(data["maximum"])
        avg_current = float(data["average"])
        
        # Validate logical order
        if min_current > max_current:
            raise ValueError(f"Minimum current {min_current} A cannot be greater than maximum {max_current} A")
        if not min_current <= avg_current <= max_current:
            raise ValueError(f"Average current {avg_current} A must be between minimum {min_current} A and maximum {max_current} A")
        
        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = 65535 * 0.01
        for name, current in [("minimum", min_current), ("maximum", max_current), ("average", avg_current)]:
            if not 0.0 <= current <= max_current_value:
                raise ValueError(f"{name.capitalize()} current {current} A is outside valid range (0.0 to {max_current_value} A)")
        
        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(min_current * 100)
        max_current_raw = round(max_current * 100)
        avg_current_raw = round(avg_current * 100)
        
        # Encode as 3 uint16 values (little endian)
        result = bytearray()
        result.extend(min_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(avg_current_raw.to_bytes(2, byteorder="little", signed=False))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
