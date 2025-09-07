"""Sound Pressure Level characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class SoundPressureLevelCharacteristic(BaseCharacteristic):
    """Power Specification characteristic (0x2B06).

    Measures power specification values.
    """

    _characteristic_name: str = "Power Specification"

    def parse_value(self, data: bytearray) -> float:
        """Parse sound pressure level data.

        Format: 2-byte signed integer representing sound level in 0.1 dB units.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Sound pressure level in dB
        """
        if len(data) < 2:
            raise ValueError("Sound Pressure Level data must be at least 2 bytes")

        # Convert sint16 (little endian) to sound level in dB
        spl_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        return spl_raw * 0.1

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dB"
