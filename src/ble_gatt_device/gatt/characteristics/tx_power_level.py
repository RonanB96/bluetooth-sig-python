"""Tx Power Level characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TxPowerLevelCharacteristic(BaseCharacteristic):
    """Tx Power Level characteristic.

    Measures transmit power level in dBm.
    """

    _characteristic_name: str = "Tx Power Level"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "int"
        super().__post_init__()

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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dBm"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "signal_strength"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
