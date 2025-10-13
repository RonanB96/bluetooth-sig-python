"""Electric Current Statistics characteristic implementation."""

from __future__ import annotations

from typing import Any

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT16_MAX
from .base import BaseCharacteristic


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


class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic):
    """Electric Current Statistics characteristic.

    Provides statistical current data (min, max, average over time).
    """

    # Override since decode_value returns structured ElectricCurrentStatisticsData
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> ElectricCurrentStatisticsData:
        """Parse current statistics data (3x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            ElectricCurrentStatisticsData with 'minimum', 'maximum', and 'average' current values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError("Electric current statistics data must be at least 6 bytes")

        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_current_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return ElectricCurrentStatisticsData(
            minimum=min_current_raw * 0.01,
            maximum=max_current_raw * 0.01,
            average=avg_current_raw * 0.01,
        )

    def encode_value(self, data: ElectricCurrentStatisticsData) -> bytearray:
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
        result.extend(min_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(avg_current_raw.to_bytes(2, byteorder="little", signed=False))

        return result
