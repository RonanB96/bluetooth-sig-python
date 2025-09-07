"""Voltage Frequency characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageFrequencyCharacteristic(BaseCharacteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _characteristic_name: str = "Voltage Frequency"

    def decode_value(self, data: bytearray) -> float:
        """Parse voltage frequency data (uint16 in units of 1/256 Hz).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Frequency value in Hz

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Voltage frequency data must be at least 2 bytes")

        # Convert uint16 (little endian) to frequency in Hz
        frequency_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return frequency_raw / 256.0

    def encode_value(self, data: float | int) -> bytearray:
        """Encode voltage frequency value back to bytes.

        Args:
            data: Voltage frequency in Hz

        Returns:
            Encoded bytes representing the frequency (uint16, 1/256 Hz resolution)
        """
        frequency = float(data)

        # Validate range for uint16 with 1/256 Hz resolution (0 to ~256 Hz)
        max_frequency = 65535 / 256.0  # ~255.996 Hz
        if not 0.0 <= frequency <= max_frequency:
            raise ValueError(
                f"Voltage frequency {frequency} Hz is outside valid range (0.0 to {max_frequency:.3f} Hz)"
            )

        # Convert Hz to raw value (multiply by 256 for 1/256 Hz resolution)
        frequency_raw = round(frequency * 256)

        return bytearray(frequency_raw.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "Hz"
