"""Voltage Specification characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageSpecificationCharacteristic(BaseCharacteristic):
    """Voltage Specification characteristic.

    Specifies minimum and maximum voltage values for electrical specifications.
    """

    _characteristic_name: str = "Voltage Specification"

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

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode voltage specification value back to bytes.

        Args:
            data: Dictionary with 'minimum' and 'maximum' voltage values in Volts

        Returns:
            Encoded bytes representing the voltage specification (2x uint16, 1/64 V resolution)
        """
        if not isinstance(data, dict):
            raise TypeError("Voltage specification data must be a dictionary")
        
        if "minimum" not in data or "maximum" not in data:
            raise ValueError("Voltage specification data must contain 'minimum' and 'maximum' keys")
        
        min_voltage = float(data["minimum"])
        max_voltage = float(data["maximum"])
        
        # Validate logical order
        if min_voltage > max_voltage:
            raise ValueError(f"Minimum voltage {min_voltage} V cannot be greater than maximum {max_voltage} V")
        
        # Validate range for uint16 with 1/64 V resolution (0 to ~1024 V)
        max_voltage_value = 65535 / 64.0  # ~1024 V
        if not 0.0 <= min_voltage <= max_voltage_value:
            raise ValueError(f"Minimum voltage {min_voltage} V is outside valid range (0.0 to {max_voltage_value:.2f} V)")
        if not 0.0 <= max_voltage <= max_voltage_value:
            raise ValueError(f"Maximum voltage {max_voltage} V is outside valid range (0.0 to {max_voltage_value:.2f} V)")
        
        # Convert Volts to raw values (multiply by 64 for 1/64 V resolution)
        min_voltage_raw = round(min_voltage * 64)
        max_voltage_raw = round(max_voltage * 64)
        
        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(min_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"
