"""Tx Power Level characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TxPowerLevelCharacteristic(BaseCharacteristic):
    """Tx Power Level characteristic.

    Measures transmit power level in dBm.
    """

    _characteristic_name: str = "Tx Power Level"

    def parse_value(self, data: bytearray) -> int:
        """Parse TX power level data (sint8 in dBm).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            TX power level in dBm

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 1:
            raise ValueError("TX power level data must be at least 1 byte")

        # Convert sint8 to power level in dBm
        power_raw = int.from_bytes(data[:1], byteorder="little", signed=True)
        return power_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode TX power level value back to bytes.

        Args:
            data: TX power level in dBm

        Returns:
            Encoded bytes representing the TX power level (sint8)
        """
        power_level = int(data)
        
        # Validate range for sint8 (-128 to 127)
        if not -128 <= power_level <= 127:
            raise ValueError(f"TX power level {power_level} dBm is outside valid range (-128 to 127 dBm)")
        
        return bytearray(power_level.to_bytes(1, byteorder="little", signed=True))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dBm"
