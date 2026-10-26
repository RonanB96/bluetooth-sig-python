"""Temperature Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, TEMPERATURE_RESOLUTION
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class TemperatureRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for temperature range.

    Each value is a temperature in degrees Celsius with 0.01°C resolution.
    """

    minimum: float  # Minimum temperature in °C
    maximum: float  # Maximum temperature in °C

    def __post_init__(self) -> None:
        """Validate temperature range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum temperature {self.minimum} °C cannot be greater than maximum {self.maximum} °C")
        temp_min = SINT16_MIN * TEMPERATURE_RESOLUTION
        temp_max = SINT16_MAX * TEMPERATURE_RESOLUTION
        for name, val in [("minimum", self.minimum), ("maximum", self.maximum)]:
            if not temp_min <= val <= temp_max:
                raise ValueError(
                    f"{name.capitalize()} temperature {val} °C is outside valid range ({temp_min} to {temp_max})"
                )


class TemperatureRangeCharacteristic(BaseCharacteristic[TemperatureRangeData]):
    """Temperature Range characteristic (0x2B10).

    org.bluetooth.characteristic.temperature_range

    Represents a temperature range as a pair of Temperature values.
    Each field is a sint16, M=1 d=-2 b=0 (resolution 0.01°C).
    """

    # Validation attributes
    expected_length: int = 4  # 2 x sint16
    min_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TemperatureRangeData:
        """Parse temperature range data (2 x sint16, 0.01°C resolution).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            TemperatureRangeData with minimum and maximum temperature values in °C.

        """
        min_raw = DataParser.parse_int16(data, 0, signed=True)
        max_raw = DataParser.parse_int16(data, 2, signed=True)

        return TemperatureRangeData(
            minimum=min_raw * TEMPERATURE_RESOLUTION,
            maximum=max_raw * TEMPERATURE_RESOLUTION,
        )

    def _encode_value(self, data: TemperatureRangeData) -> bytearray:
        """Encode temperature range to bytes.

        Args:
            data: TemperatureRangeData instance.

        Returns:
            Encoded bytes (2 x sint16, little-endian).

        """
        if not isinstance(data, TemperatureRangeData):
            raise TypeError(f"Expected TemperatureRangeData, got {type(data).__name__}")

        min_raw = round(data.minimum / TEMPERATURE_RESOLUTION)
        max_raw = round(data.maximum / TEMPERATURE_RESOLUTION)

        for name, value in [("minimum", min_raw), ("maximum", max_raw)]:
            if not SINT16_MIN <= value <= SINT16_MAX:
                raise ValueError(f"Temperature {name} raw value {value} exceeds sint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(min_raw, signed=True))
        result.extend(DataParser.encode_int16(max_raw, signed=True))
        return result
