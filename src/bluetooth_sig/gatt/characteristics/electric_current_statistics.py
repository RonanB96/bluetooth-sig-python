"""Electric Current Statistics characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ElectricCurrentStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for electric current statistics."""

    minimum: float  # Minimum current in Amperes
    maximum: float  # Maximum current in Amperes
    average: float  # Average current in Amperes

    def __post_init__(self) -> None:
        """Validate current statistics data."""
        # Validate logical order
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A")
        if not self.minimum <= self.average <= self.maximum:
            raise ValueError(
                f"Average current {self.average} A must be between "
                f"minimum {self.minimum} A and maximum {self.maximum} A"
            )

        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = UINT16_MAX * 0.01
        for name, current in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("average", self.average),
        ]:
            if not 0.0 <= current <= max_current_value:
                raise ValueError(
                    f"{name.capitalize()} current {current} A is outside valid range (0.0 to {max_current_value} A)"
                )


class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic[ElectricCurrentStatisticsData]):
    """Electric Current Statistics characteristic (0x2AF1).

    org.bluetooth.characteristic.electric_current_statistics

    Electric Current Statistics characteristic.

    Provides statistical current data (min, max, average over time).
    """

    # Validation attributes
    expected_length: int = 6  # 3x uint16
    min_length: int = 6

    # Override since decode_value returns structured ElectricCurrentStatisticsData
    _python_type: type | str | None = dict

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ElectricCurrentStatisticsData:
        """Parse current statistics data (3x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            ElectricCurrentStatisticsData with 'minimum', 'maximum', and 'average' current values in Amperes.

        Raises:
            ValueError: If data is insufficient.

        """
        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = DataParser.parse_int16(data, 0, signed=False)
        max_current_raw = DataParser.parse_int16(data, 2, signed=False)
        avg_current_raw = DataParser.parse_int16(data, 4, signed=False)

        return ElectricCurrentStatisticsData(
            minimum=min_current_raw * 0.01,
            maximum=max_current_raw * 0.01,
            average=avg_current_raw * 0.01,
        )

    def _encode_value(self, data: ElectricCurrentStatisticsData) -> bytearray:
        """Encode electric current statistics value back to bytes.

        Args:
            data: ElectricCurrentStatisticsData instance

        Returns:
            Encoded bytes representing the current statistics (3x uint16, 0.01 A resolution)

        """
        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(data.minimum * 100)
        max_current_raw = round(data.maximum * 100)
        avg_current_raw = round(data.average * 100)

        # Encode as 3 uint16 values (little endian)
        result = bytearray()
        result.extend(DataParser.encode_int16(min_current_raw, signed=False))
        result.extend(DataParser.encode_int16(max_current_raw, signed=False))
        result.extend(DataParser.encode_int16(avg_current_raw, signed=False))

        return result
