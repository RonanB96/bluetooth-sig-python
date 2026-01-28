"""Voltage Statistics characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VoltageStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for voltage statistics."""

    minimum: float  # Minimum voltage in Volts
    maximum: float  # Maximum voltage in Volts
    average: float  # Average voltage in Volts

    def __post_init__(self) -> None:
        """Validate voltage statistics data."""
        # Validate logical order
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum voltage {self.minimum} V cannot be greater than maximum {self.maximum} V")
        if not self.minimum <= self.average <= self.maximum:
            raise ValueError(
                f"Average voltage {self.average} V must be between "
                f"minimum {self.minimum} V and maximum {self.maximum} V"
            )

        # Validate range for uint16 with 1/64 V resolution (0 to ~1024 V)
        max_voltage_value = UINT16_MAX / 64.0  # ~1024 V
        for name, voltage in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("average", self.average),
        ]:
            if not 0.0 <= voltage <= max_voltage_value:
                raise ValueError(
                    f"{name.capitalize()} voltage {voltage} V is outside valid range (0.0 to {max_voltage_value:.2f} V)"
                )


class VoltageStatisticsCharacteristic(BaseCharacteristic[VoltageStatisticsData]):
    """Voltage Statistics characteristic (0x2B1A).

    org.bluetooth.characteristic.voltage_statistics

    Voltage Statistics characteristic.

    Provides statistical voltage data over time.
    """

    # Override since decode_value returns structured VoltageStatisticsData
    _manual_value_type: ValueType | str | None = ValueType.DICT
    expected_length: int = 6  # Minimum(2) + Maximum(2) + Average(2)
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoltageStatisticsData:
        """Parse voltage statistics data (3x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            VoltageStatisticsData with 'minimum', 'maximum', and 'average' voltage values in Volts.

        # `ctx` is intentionally unused for this characteristic; mark as used for linters.
        del ctx
        Raises:
            ValueError: If data is insufficient.

        """
        # Convert 3x uint16 (little endian) to voltage statistics in Volts
        min_voltage_raw = DataParser.parse_int16(data, 0, signed=False)
        max_voltage_raw = DataParser.parse_int16(data, 2, signed=False)
        avg_voltage_raw = DataParser.parse_int16(data, 4, signed=False)

        return VoltageStatisticsData(
            minimum=min_voltage_raw / 64.0,
            maximum=max_voltage_raw / 64.0,
            average=avg_voltage_raw / 64.0,
        )

    def _encode_value(self, data: VoltageStatisticsData) -> bytearray:
        """Encode voltage statistics value back to bytes.

        Args:
            data: VoltageStatisticsData instance with 'minimum', 'maximum', and 'average' voltage values in Volts

        Returns:
            Encoded bytes representing the voltage statistics (3x uint16, 1/64 V resolution)

        """
        if not isinstance(data, VoltageStatisticsData):
            raise TypeError(f"Voltage statistics data must be a VoltageStatisticsData, got {type(data).__name__}")

        # Convert Volts to raw values (multiply by 64 for 1/64 V resolution)
        min_voltage_raw = round(data.minimum * 64)
        max_voltage_raw = round(data.maximum * 64)
        avg_voltage_raw = round(data.average * 64)

        # Validate range for uint16 (0 to UINT16_MAX)
        # pylint: disable=duplicate-code
        # NOTE: This uint16 validation and encoding pattern is shared with VoltageSpecificationCharacteristic.
        # Both characteristics encode voltage values using the same 1/64V resolution and uint16 little-endian format
        # per Bluetooth SIG spec. Consolidation not practical as each has different field structures (2 vs 3 values).
        for name, value in [
            ("minimum", min_voltage_raw),
            ("maximum", max_voltage_raw),
            ("average", avg_voltage_raw),
        ]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Voltage {name} value {value} exceeds uint16 range")

        # Encode as 3 uint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(min_voltage_raw, signed=False))
        result.extend(DataParser.encode_int16(max_voltage_raw, signed=False))
        result.extend(DataParser.encode_int16(avg_voltage_raw, signed=False))

        return result
