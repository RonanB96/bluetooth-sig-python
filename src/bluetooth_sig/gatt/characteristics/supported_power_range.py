"""Supported Power Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import SINT16_MAX, SINT16_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SupportedPowerRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported power range."""

    minimum: int  # Minimum power in Watts
    maximum: int  # Maximum power in Watts

    def __post_init__(self) -> None:
        """Validate power range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum power {self.minimum} W cannot be greater than maximum {self.maximum} W")

        # Validate range for sint16 (SINT16_MIN to SINT16_MAX)
        if not SINT16_MIN <= self.minimum <= SINT16_MAX:
            raise ValueError(f"Minimum power {self.minimum} W is outside valid range (SINT16_MIN to SINT16_MAX W)")
        if not SINT16_MIN <= self.maximum <= SINT16_MAX:
            raise ValueError(f"Maximum power {self.maximum} W is outside valid range (SINT16_MIN to SINT16_MAX W)")


class SupportedPowerRangeCharacteristic(BaseCharacteristic):
    """Supported Power Range characteristic (0x2AD8).

    org.bluetooth.characteristic.supported_power_range

    Supported Power Range characteristic.

    Specifies minimum and maximum power values for power capability
    specification.
    """

    min_length = 4
    _characteristic_name: str = "Supported Power Range"
    # Override since decode_value returns structured SupportedPowerRangeData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> SupportedPowerRangeData:
        """Parse supported power range data (2x sint16 in watts).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            SupportedPowerRangeData with minimum and maximum power values in Watts.

        Raises:
            ValueError: If data is insufficient.

        """
        if len(data) < 4:
            raise ValueError("Supported power range data must be at least 4 bytes")

        # Convert 2x sint16 (little endian) to power range in Watts
        min_power_raw = DataParser.parse_int16(data, 0, signed=True)
        max_power_raw = DataParser.parse_int16(data, 2, signed=True)

        return SupportedPowerRangeData(minimum=min_power_raw, maximum=max_power_raw)

    def encode_value(self, data: SupportedPowerRangeData) -> bytearray:
        """Encode supported power range value back to bytes.

        Args:
            data: SupportedPowerRangeData instance with 'minimum' and 'maximum' power values in Watts

        Returns:
            Encoded bytes representing the power range (2x sint16)

        """
        if not isinstance(data, SupportedPowerRangeData):
            raise TypeError(f"Supported power range data must be a SupportedPowerRangeData, got {type(data).__name__}")

        # Validate range for sint16 (SINT16_MIN to SINT16_MAX)
        if not SINT16_MIN <= data.minimum <= SINT16_MAX:
            raise ValueError(f"Minimum power {data.minimum} exceeds sint16 range")
        if not SINT16_MIN <= data.maximum <= SINT16_MAX:
            raise ValueError(f"Maximum power {data.maximum} exceeds sint16 range")
        # Encode as 2 sint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(data.minimum, signed=True))
        result.extend(DataParser.encode_int16(data.maximum, signed=True))

        return result
