"""Electric Current Specification characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic):
    """Electric Current Specification characteristic.

    Specifies minimum and maximum current values for electrical specifications.
    """

    _characteristic_name: str = "Electric Current Specification"

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse current specification data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum' and 'maximum' current specification values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError(
                "Electric current specification data must be at least 4 bytes"
            )

        # Convert 2x uint16 (little endian) to current specification in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return {"minimum": min_current_raw * 0.01, "maximum": max_current_raw * 0.01}

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode electric current specification value back to bytes.

        Args:
            data: Dictionary with 'minimum' and 'maximum' current values in Amperes

        Returns:
            Encoded bytes representing the current specification (2x uint16, 0.01 A resolution)
        """
        if not isinstance(data, dict):
            raise TypeError("Electric current specification data must be a dictionary")
        
        if "minimum" not in data or "maximum" not in data:
            raise ValueError("Electric current specification data must contain 'minimum' and 'maximum' keys")
        
        min_current = float(data["minimum"])
        max_current = float(data["maximum"])
        
        # Validate logical order
        if min_current > max_current:
            raise ValueError(f"Minimum current {min_current} A cannot be greater than maximum {max_current} A")
        
        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = 65535 * 0.01
        if not 0.0 <= min_current <= max_current_value:
            raise ValueError(f"Minimum current {min_current} A is outside valid range (0.0 to {max_current_value} A)")
        if not 0.0 <= max_current <= max_current_value:
            raise ValueError(f"Maximum current {max_current} A is outside valid range (0.0 to {max_current_value} A)")
        
        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(min_current * 100)
        max_current_raw = round(max_current * 100)
        
        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(min_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_current_raw.to_bytes(2, byteorder="little", signed=False))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
