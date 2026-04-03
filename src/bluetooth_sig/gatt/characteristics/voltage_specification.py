"""Voltage Specification characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_VOLTAGE_RESOLUTION = 1 / 64.0  # 1/64 V per raw unit
_MAX_VOLTAGE = UINT16_MAX * _VOLTAGE_RESOLUTION  # ~1023.98 V


class VoltageSpecificationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for voltage specification.

    Three voltage values (1/64 V resolution): Minimum, Typical, Maximum.
    """

    minimum: float  # Minimum voltage in Volts
    typical: float  # Typical voltage in Volts
    maximum: float  # Maximum voltage in Volts

    def __post_init__(self) -> None:
        """Validate voltage specification data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum voltage {self.minimum} V cannot be greater than maximum {self.maximum} V")

        for name, voltage in [
            ("minimum", self.minimum),
            ("typical", self.typical),
            ("maximum", self.maximum),
        ]:
            if not 0.0 <= voltage <= _MAX_VOLTAGE:
                raise ValueError(
                    f"{name.capitalize()} voltage {voltage} V is outside valid range (0.0 to {_MAX_VOLTAGE:.2f} V)"
                )


class VoltageSpecificationCharacteristic(BaseCharacteristic[VoltageSpecificationData]):
    """Voltage Specification characteristic (0x2B19).

    org.bluetooth.characteristic.voltage_specification

    Specifies minimum, typical, and maximum voltage values (uint16, 1/64 V resolution).
    """

    expected_length: int = 6  # 3x uint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoltageSpecificationData:
        """Parse voltage specification data (3x uint16 in units of 1/64 V)."""
        min_voltage_raw = DataParser.parse_int16(data, 0, signed=False)
        typical_voltage_raw = DataParser.parse_int16(data, 2, signed=False)
        max_voltage_raw = DataParser.parse_int16(data, 4, signed=False)

        return VoltageSpecificationData(
            minimum=min_voltage_raw / 64.0,
            typical=typical_voltage_raw / 64.0,
            maximum=max_voltage_raw / 64.0,
        )

    def _encode_value(self, data: VoltageSpecificationData) -> bytearray:
        """Encode voltage specification value back to bytes."""
        if not isinstance(data, VoltageSpecificationData):
            raise TypeError(f"Voltage specification data must be a VoltageSpecificationData, got {type(data).__name__}")

        min_voltage_raw = round(data.minimum * 64)
        typical_voltage_raw = round(data.typical * 64)
        max_voltage_raw = round(data.maximum * 64)

        # pylint: disable=duplicate-code
        for name, value in [
            ("minimum", min_voltage_raw),
            ("typical", typical_voltage_raw),
            ("maximum", max_voltage_raw),
        ]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Voltage {name} value {value} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(min_voltage_raw, signed=False))
        result.extend(DataParser.encode_int16(typical_voltage_raw, signed=False))
        result.extend(DataParser.encode_int16(max_voltage_raw, signed=False))

        return result
