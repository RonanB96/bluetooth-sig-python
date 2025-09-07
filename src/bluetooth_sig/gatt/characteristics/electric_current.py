"""Electric Current characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentCharacteristic(BaseCharacteristic):
    """Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Electric Current"

    def parse_value(self, data: bytearray) -> float:
        """Parse electric current data (uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Current value in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Electric current data must be at least 2 bytes")

        # Convert uint16 (little endian) to current in Amperes
        current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return current_raw * 0.01

    def encode_value(self, data: float | int) -> bytearray:
        """Encode electric current value back to bytes.

        Args:
            data: Electric current value in Amperes

        Returns:
            Encoded bytes representing the current (uint16, 0.01 A resolution)
        """
        current = float(data)
        
        # Validate range (reasonable current range for uint16 with 0.01 resolution)
        max_current = 65535 * 0.01  # 655.35 A
        if not 0.0 <= current <= max_current:
            raise ValueError(f"Electric current {current} A is outside valid range (0.0 to {max_current} A)")
        
        # Convert Amperes to raw value (multiply by 100 for 0.01 A resolution)
        current_raw = round(current * 100)
        
        return bytearray(current_raw.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
