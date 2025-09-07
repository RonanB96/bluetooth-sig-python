"""Voltage Statistics characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageStatisticsCharacteristic(BaseCharacteristic):
    """Voltage Statistics characteristic.

    Provides statistical voltage data over time.
    """

    _characteristic_name: str = "Voltage Statistics"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse voltage statistics data (3x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum', 'maximum', and 'average' voltage values in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError("Voltage statistics data must be at least 6 bytes")

        # Convert 3x uint16 (little endian) to voltage statistics in Volts
        min_voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_voltage_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_voltage_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return {
            "minimum": min_voltage_raw / 64.0,
            "maximum": max_voltage_raw / 64.0,
            "average": avg_voltage_raw / 64.0,
        }

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode voltage statistics value back to bytes.

        Args:
            data: Dictionary with 'minimum', 'maximum', and 'average' voltage values in Volts

        Returns:
            Encoded bytes representing the voltage statistics (3x uint16, 1/64 V resolution)
        """
        if not isinstance(data, dict):
            raise TypeError("Voltage statistics data must be a dictionary")
        
        if "minimum" not in data or "maximum" not in data or "average" not in data:
            raise ValueError("Voltage statistics data must contain 'minimum', 'maximum', and 'average' keys")
        
        min_voltage = float(data["minimum"])
        max_voltage = float(data["maximum"])
        avg_voltage = float(data["average"])
        
        # Validate logical order
        if min_voltage > max_voltage:
            raise ValueError(f"Minimum voltage {min_voltage} V cannot be greater than maximum {max_voltage} V")
        if not min_voltage <= avg_voltage <= max_voltage:
            raise ValueError(f"Average voltage {avg_voltage} V must be between minimum {min_voltage} V and maximum {max_voltage} V")
        
        # Validate range for uint16 with 1/64 V resolution (0 to ~1024 V)
        max_voltage_value = 65535 / 64.0  # ~1024 V
        for name, voltage in [("minimum", min_voltage), ("maximum", max_voltage), ("average", avg_voltage)]:
            if not 0.0 <= voltage <= max_voltage_value:
                raise ValueError(f"{name.capitalize()} voltage {voltage} V is outside valid range (0.0 to {max_voltage_value:.2f} V)")
        
        # Convert Volts to raw values (multiply by 64 for 1/64 V resolution)
        min_voltage_raw = round(min_voltage * 64)
        max_voltage_raw = round(max_voltage * 64)
        avg_voltage_raw = round(avg_voltage * 64)
        
        # Encode as 3 uint16 values (little endian)
        result = bytearray()
        result.extend(min_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(avg_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"
