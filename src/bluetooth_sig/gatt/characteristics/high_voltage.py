"""High Voltage characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HighVoltageCharacteristic(BaseCharacteristic):
    """High Voltage characteristic.

    Measures high voltage systems using uint24 format.
    """

    _characteristic_name: str = "High Voltage"

    def parse_value(self, data: bytearray) -> float:
        """Parse high voltage data (uint24 for high voltage systems).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            High voltage value in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 3:
            raise ValueError("High voltage data must be at least 3 bytes")

        # Convert uint24 (little endian) to voltage in Volts
        # Add padding byte for uint32 conversion
        voltage_data = data[:3] + b"\x00"
        voltage_raw = int.from_bytes(voltage_data, byteorder="little", signed=False)
        return float(voltage_raw)

    def encode_value(self, data: float | int) -> bytearray:
        """Encode high voltage value back to bytes.

        Args:
            data: High voltage value in Volts

        Returns:
            Encoded bytes representing the high voltage (uint24, 1 V resolution)
        """
        voltage = float(data)
        
        # Validate range for uint24 (0 to 16777215 V)
        if not 0.0 <= voltage <= 16777215.0:
            raise ValueError(f"High voltage {voltage} V is outside valid range (0.0 to 16777215.0 V)")
        
        # Convert to raw value (already in whole volts)
        voltage_raw = round(voltage)
        
        # Encode as 3 bytes (little endian)
        return bytearray(voltage_raw.to_bytes(3, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"
