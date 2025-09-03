"""Voltage Specification characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageSpecificationCharacteristic(BaseCharacteristic):
    """Voltage Specification characteristic.

    Specifies minimum and maximum voltage values for electrical specifications.
    """

    _characteristic_name: str = "Voltage Specification"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse voltage specification data (2x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum' and 'maximum' voltage specification values in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError("Voltage specification data must be at least 4 bytes")

        # Convert 2x uint16 (little endian) to voltage specification in Volts
        min_voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_voltage_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return {"minimum": min_voltage_raw / 64.0, "maximum": max_voltage_raw / 64.0}

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "voltage"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Specification data doesn't have a standard state class
