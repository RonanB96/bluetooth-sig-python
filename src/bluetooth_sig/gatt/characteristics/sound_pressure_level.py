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

    def encode_value(self, data: float | int) -> bytearray:
        """Encode sound pressure level value back to bytes.

        Args:
            data: Sound pressure level in dB

        Returns:
            Encoded bytes representing the sound pressure level (sint16, 0.1 dB resolution)
        """
        spl = float(data)
        
        # Validate range for sint16 with 0.1 dB resolution (-3276.8 to 3276.7 dB)
        if not -3276.8 <= spl <= 3276.7:
            raise ValueError(f"Sound pressure level {spl} dB is outside valid range (-3276.8 to 3276.7 dB)")
        
        # Convert dB to raw value (multiply by 10 for 0.1 dB resolution)
        spl_raw = round(spl * 10)
        
        return bytearray(spl_raw.to_bytes(2, byteorder="little", signed=True))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dB"
