"""Event Statistics characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_TIME_EXP_BASE = 1.1
_TIME_EXP_OFFSET = 64


def _decode_time_exponential(raw: int) -> float:
    """Decode Time Exponential 8 raw value to seconds."""
    if raw == 0:
        return 0.0
    return _TIME_EXP_BASE ** (raw - _TIME_EXP_OFFSET)


def _encode_time_exponential(seconds: float) -> int:
    """Encode seconds to Time Exponential 8 raw value."""
    if seconds <= 0.0:
        return 0
    n = round(math.log(seconds) / math.log(_TIME_EXP_BASE) + _TIME_EXP_OFFSET)
    return max(1, min(n, 0xFD))


class EventStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for event statistics.

    Event count (uint16), average event duration (uint16, seconds),
    time elapsed since last event (Time Exponential 8, seconds),
    and sensing duration (Time Exponential 8, seconds).
    """

    number_of_events: int  # Count 16 (unitless)
    average_event_duration: int  # Time Second 16 (seconds, integer)
    time_elapsed_since_last_event: float  # Time Exponential 8 (seconds)
    sensing_duration: float  # Time Exponential 8 (seconds)

    def __post_init__(self) -> None:
        """Validate data fields."""
        if not 0 <= self.number_of_events <= UINT16_MAX:
            raise ValueError(f"Number of events {self.number_of_events} is outside valid range (0 to {UINT16_MAX})")
        if not 0 <= self.average_event_duration <= UINT16_MAX:
            raise ValueError(
                f"Average event duration {self.average_event_duration} s is outside valid range (0 to {UINT16_MAX})"
            )
        if self.time_elapsed_since_last_event < 0.0:
            raise ValueError(f"Time elapsed {self.time_elapsed_since_last_event} s cannot be negative")
        if self.sensing_duration < 0.0:
            raise ValueError(f"Sensing duration {self.sensing_duration} s cannot be negative")


class EventStatisticsCharacteristic(BaseCharacteristic[EventStatisticsData]):
    """Event Statistics characteristic (0x2AF4).

    org.bluetooth.characteristic.event_statistics

    Statistics for events: count (uint16), average duration (uint16, 1 s),
    time since last event (Time Exponential 8), sensing duration
    (Time Exponential 8).
    """

    expected_length: int = 6  # 2 x uint16 + 2 x uint8
    min_length: int = 6
    expected_type = EventStatisticsData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> EventStatisticsData:
        """Parse event statistics.

        Args:
            data: Raw bytes (6 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            EventStatisticsData.

        """
        count = DataParser.parse_int16(data, 0, signed=False)
        avg_dur = DataParser.parse_int16(data, 2, signed=False)
        elapsed_raw = DataParser.parse_int8(data, 4, signed=False)
        duration_raw = DataParser.parse_int8(data, 5, signed=False)

        return EventStatisticsData(
            number_of_events=count,
            average_event_duration=avg_dur,
            time_elapsed_since_last_event=_decode_time_exponential(elapsed_raw),
            sensing_duration=_decode_time_exponential(duration_raw),
        )

    def _encode_value(self, data: EventStatisticsData) -> bytearray:
        """Encode event statistics.

        Args:
            data: EventStatisticsData instance.

        Returns:
            Encoded bytes (6 bytes).

        """
        elapsed_raw = _encode_time_exponential(data.time_elapsed_since_last_event)
        duration_raw = _encode_time_exponential(data.sensing_duration)

        if not 0 <= data.number_of_events <= UINT16_MAX:
            raise ValueError(f"Event count {data.number_of_events} exceeds uint16 range")
        if not 0 <= data.average_event_duration <= UINT16_MAX:
            raise ValueError(f"Average duration {data.average_event_duration} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(data.number_of_events, signed=False))
        result.extend(DataParser.encode_int16(data.average_event_duration, signed=False))
        result.extend(DataParser.encode_int8(elapsed_raw, signed=False))
        result.extend(DataParser.encode_int8(duration_raw, signed=False))
        return result
