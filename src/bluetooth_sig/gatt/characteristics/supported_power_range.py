"""Supported Power Range characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class SupportedPowerRangeCharacteristic(BaseCharacteristic):
    """Supported Power Range characteristic.

    Specifies minimum and maximum power values for power capability specification.
    """

    _characteristic_name: str = "Supported Power Range"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, int]:
        """Parse supported power range data (2x sint16 in watts).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum' and 'maximum' power values in Watts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError("Supported power range data must be at least 4 bytes")

        # Convert 2x sint16 (little endian) to power range in Watts
        min_power_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        max_power_raw = int.from_bytes(data[2:4], byteorder="little", signed=True)

        return {"minimum": min_power_raw, "maximum": max_power_raw}

    def encode_value(self, data: dict[str, int]) -> bytearray:
        """Encode supported power range value back to bytes.

        Args:
            data: Dictionary with 'minimum' and 'maximum' power values in Watts

        Returns:
            Encoded bytes representing the power range (2x sint16)
        """
        if not isinstance(data, dict):
            raise TypeError("Supported power range data must be a dictionary")
        
        if "minimum" not in data or "maximum" not in data:
            raise ValueError("Supported power range data must contain 'minimum' and 'maximum' keys")
        
        min_power = int(data["minimum"])
        max_power = int(data["maximum"])
        
        # Validate logical order
        if min_power > max_power:
            raise ValueError(f"Minimum power {min_power} W cannot be greater than maximum {max_power} W")
        
        # Validate range for sint16 (-32768 to 32767)
        if not -32768 <= min_power <= 32767:
            raise ValueError(f"Minimum power {min_power} W is outside valid range (-32768 to 32767 W)")
        if not -32768 <= max_power <= 32767:
            raise ValueError(f"Maximum power {max_power} W is outside valid range (-32768 to 32767 W)")
        
        # Encode as 2 sint16 values (little endian)
        result = bytearray()
        result.extend(min_power.to_bytes(2, byteorder="little", signed=True))
        result.extend(max_power.to_bytes(2, byteorder="little", signed=True))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "W"
