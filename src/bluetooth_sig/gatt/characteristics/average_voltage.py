"""Average Voltage characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class AverageVoltageCharacteristic(BaseCharacteristic):
    """Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Average Voltage"

    def parse_value(self, data: bytearray) -> float:
        """Parse average voltage data (uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Average voltage value in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Average voltage data must be at least 2 bytes")

        # Convert uint16 (little endian) to voltage in Volts
        voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return voltage_raw / 64.0

    def encode_value(self, data: float | int) -> bytearray:
        """Encode average voltage value back to bytes.

        Args:
            data: Average voltage value in Volts

        Returns:
            Encoded bytes representing the average voltage (uint16, 1/64 V resolution)
        """
        voltage = float(data)

        # Validate range (reasonable voltage range for uint16 with 1/64 resolution)
        max_voltage = 65535 / 64.0  # ~1024 V
        if not 0.0 <= voltage <= max_voltage:
            raise ValueError(
                f"Average voltage {voltage} V is outside valid range (0.0 to {max_voltage:.2f} V)"
            )

        # Convert Volts to raw value (multiply by 64 for 1/64 V resolution)
        voltage_raw = round(voltage * 64)

        return bytearray(voltage_raw.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"
