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


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dBm"
