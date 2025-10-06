"""Voltage Specification characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from .base import BaseCharacteristic


@dataclass
class VoltageSpecificationData:
    """Data class for voltage specification."""

    minimum: float  # Minimum voltage in Volts
    maximum: float  # Maximum voltage in Volts

    def __post_init__(self) -> None:
        """Validate voltage specification data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum voltage {self.minimum} V cannot be greater than maximum {self.maximum} V")

        # Validate range for uint16 with 1/64 V resolution (0 to ~1024 V)
        max_voltage_value = UINT16_MAX / 64.0  # ~1024 V
        if not 0.0 <= self.minimum <= max_voltage_value:
            raise ValueError(
                f"Minimum voltage {self.minimum} V is outside valid range (0.0 to {max_voltage_value:.2f} V)"
            )
        if not 0.0 <= self.maximum <= max_voltage_value:
            raise ValueError(
                f"Maximum voltage {self.maximum} V is outside valid range (0.0 to {max_voltage_value:.2f} V)"
            )


class VoltageSpecificationCharacteristic(BaseCharacteristic):
    """Voltage Specification characteristic.

    Specifies minimum and maximum voltage values for electrical
    specifications.
    """

    _characteristic_name: str = "Voltage Specification"
    # Override since decode_value returns structured VoltageSpecificationData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> VoltageSpecificationData:
        """Parse voltage specification data (2x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            VoltageSpecificationData with 'minimum' and 'maximum' voltage specification values in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError("Voltage specification data must be at least 4 bytes")

        # Convert 2x uint16 (little endian) to voltage specification in Volts
        min_voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_voltage_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return VoltageSpecificationData(minimum=min_voltage_raw / 64.0, maximum=max_voltage_raw / 64.0)

    def encode_value(self, data: VoltageSpecificationData) -> bytearray:
        """Encode voltage specification value back to bytes.

        Args:
            data: VoltageSpecificationData instance with 'minimum' and 'maximum' voltage values in Volts

        Returns:
            Encoded bytes representing the voltage specification (2x uint16, 1/64 V resolution)
        """
        if not isinstance(data, VoltageSpecificationData):
            raise TypeError(f"Voltage specification data must be a VoltageSpecificationData, got {type(data).__name__}")
            # Convert Volts to raw values (multiply by 64 for 1/64 V resolution)
        min_voltage_raw = round(data.minimum * 64)
        max_voltage_raw = round(data.maximum * 64)

        # Validate range for uint16 (0 to UINT16_MAX)
        for name, value in [("minimum", min_voltage_raw), ("maximum", max_voltage_raw)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Voltage {name} value {value} exceeds uint16 range")

        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(min_voltage_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_voltage_raw.to_bytes(2, byteorder="little", signed=False))

        return result
