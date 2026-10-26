"""Relative Value in a Period of Day characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
_TIME_DECIHOUR_RESOLUTION = 0.1  # Time Decihour 8: M=1, d=-1, b=0 -> 0.1 hr


class RelativeValueInAPeriodOfDayData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative value in a period of day.

    Combines a percentage (0.5% resolution) with a time-of-day range
    (start/end in hours, 0.1 hr resolution).
    """

    relative_value: float  # Percentage (0.5% resolution)
    start_time: float  # Start time in hours (0.1 hr resolution)
    end_time: float  # End time in hours (0.1 hr resolution)

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_value <= max_pct:
            raise ValueError(f"Relative value {self.relative_value}% is outside valid range (0.0 to {max_pct})")
        max_time = UINT8_MAX * _TIME_DECIHOUR_RESOLUTION
        for name, val in [("start_time", self.start_time), ("end_time", self.end_time)]:
            if not 0.0 <= val <= max_time:
                raise ValueError(f"{name} {val} hr is outside valid range (0.0 to {max_time})")


class RelativeValueInAPeriodOfDayCharacteristic(
    BaseCharacteristic[RelativeValueInAPeriodOfDayData],
):
    """Relative Value in a Period of Day characteristic (0x2B0B).

    org.bluetooth.characteristic.relative_value_in_a_period_of_day

    Represents a relative value within a period of the day. Fields:
    Percentage 8 (uint8, 0.5%), start time (uint8, 0.1 hr),
    end time (uint8, 0.1 hr).
    """

    expected_length: int = 3  # 3 x uint8
    min_length: int = 3
    expected_type = RelativeValueInAPeriodOfDayData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeValueInAPeriodOfDayData:
        """Parse relative value in a period of day.

        Args:
            data: Raw bytes (3 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeValueInAPeriodOfDayData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        start_raw = DataParser.parse_int8(data, 1, signed=False)
        end_raw = DataParser.parse_int8(data, 2, signed=False)

        return RelativeValueInAPeriodOfDayData(
            relative_value=pct_raw * _PERCENTAGE_RESOLUTION,
            start_time=start_raw * _TIME_DECIHOUR_RESOLUTION,
            end_time=end_raw * _TIME_DECIHOUR_RESOLUTION,
        )

    def _encode_value(self, data: RelativeValueInAPeriodOfDayData) -> bytearray:
        """Encode relative value in a period of day.

        Args:
            data: RelativeValueInAPeriodOfDayData instance.

        Returns:
            Encoded bytes (3 bytes).

        """
        pct_raw = round(data.relative_value / _PERCENTAGE_RESOLUTION)
        start_raw = round(data.start_time / _TIME_DECIHOUR_RESOLUTION)
        end_raw = round(data.end_time / _TIME_DECIHOUR_RESOLUTION)

        for name, value in [
            ("percentage", pct_raw),
            ("start_time", start_raw),
            ("end_time", end_raw),
        ]:
            if not 0 <= value <= UINT8_MAX:
                raise ValueError(f"{name} raw value {value} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int8(start_raw, signed=False))
        result.extend(DataParser.encode_int8(end_raw, signed=False))
        return result
