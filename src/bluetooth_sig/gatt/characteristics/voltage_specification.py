"""Voltage Specification characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VoltageSpecificationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
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


class VoltageSpecificationCharacteristic(BaseCharacteristic[VoltageSpecificationData]):
    """Voltage Specification characteristic (0x2B19).

    org.bluetooth.characteristic.voltage_specification

    Voltage Specification characteristic.

    Specifies minimum and maximum voltage values for electrical
    specifications.
    """

    min_length = 4
    # Override since decode_value returns structured VoltageSpecificationData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoltageSpecificationData:
        """Parse voltage specification data (2x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            VoltageSpecificationData with 'minimum' and 'maximum' voltage specification values in Volts.

        Raises:
            ValueError: If data is insufficient.

        """
        # Convert 2x uint16 (little endian) to voltage specification in Volts
        min_voltage_raw = DataParser.parse_int16(data, 0, signed=False)
        max_voltage_raw = DataParser.parse_int16(data, 2, signed=False)

        return VoltageSpecificationData(minimum=min_voltage_raw / 64.0, maximum=max_voltage_raw / 64.0)

    def _encode_value(self, data: VoltageSpecificationData) -> bytearray:
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
        #  pylint: disable=duplicate-code
        # NOTE: This uint16 validation and encoding pattern is shared with VoltageStatisticsCharacteristic.
        # Both characteristics encode voltage values using the same 1/64V resolution and uint16 little-endian format
        # per Bluetooth SIG spec. Consolidation not practical as each has different field structures.
        for name, value in [("minimum", min_voltage_raw), ("maximum", max_voltage_raw)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Voltage {name} value {value} exceeds uint16 range")

        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(min_voltage_raw, signed=False))
        result.extend(DataParser.encode_int16(max_voltage_raw, signed=False))

        return result
