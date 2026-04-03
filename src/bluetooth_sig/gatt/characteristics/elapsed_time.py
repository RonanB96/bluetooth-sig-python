"""Elapsed Time characteristic implementation.

Implements the Elapsed Time characteristic (0x2BF2).

Structure (from GSS YAML - org.bluetooth.characteristic.elapsed_time):
    Flags (uint8, 1 byte) -- interpretation flags
    Time Value (uint48, 6 bytes) -- counter in time-resolution units
    Time Sync Source Type (uint8, 1 byte) -- sync source enum
    TZ/DST Offset (sint8, 1 byte) -- combined offset in 15-minute units

Note: The GSS YAML identifier is ``elapsed_time`` but the UUID registry
identifier is ``current_elapsed_time`` (0x2BF2). File is named to match
the UUID registry for auto-discovery.

Flag bits:
    0: Tick counter (0=time of day, 1=relative counter)
    1: UTC (0=local time, 1=UTC) — meaningless for tick counter
    2-3: Time resolution (00=1s, 01=100ms, 10=1ms, 11=100µs)
    4: TZ/DST offset used (0=not used, 1=used)
    5: Current timeline (0=not current, 1=current)
    6-7: Reserved

References:
    Bluetooth SIG Generic Sensor Service
    org.bluetooth.characteristic.elapsed_time (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .reference_time_information import TimeSource
from .utils import DataParser

_TIME_RESOLUTION_MASK = 0x0C
_TIME_RESOLUTION_SHIFT = 2
_READ_LENGTH = 11  # 9 (Elapsed Time struct) + 1 (Clock Status) + 1 (Clock Capabilities)


class ElapsedTimeFlags(IntFlag):
    """Flags for the Elapsed Time characteristic."""

    TICK_COUNTER = 1 << 0
    UTC = 1 << 1
    TZ_DST_USED = 1 << 4
    CURRENT_TIMELINE = 1 << 5


class TimeResolution(IntEnum):
    """Time resolution values (bits 2-3 of flags)."""

    ONE_SECOND = 0
    HUNDRED_MILLISECONDS = 1
    ONE_MILLISECOND = 2
    HUNDRED_MICROSECONDS = 3


class ElapsedTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Current Elapsed Time characteristic.

    Attributes:
        flags: Interpretation flags.
        time_value: Counter value in the resolution defined by flags.
        time_resolution: Resolution of the time value.
        is_tick_counter: True if time_value is a relative counter.
        is_utc: True if time_value reports UTC (only meaningful if not tick counter).
        tz_dst_used: True if tz_dst_offset is meaningful.
        is_current_timeline: True if time stamp is from the current timeline.
        sync_source_type: Time synchronisation source type.
        tz_dst_offset: Combined TZ/DST offset from UTC in 15-minute units.
        clock_needs_set: Server requests client to set the clock (Clock Status bit 0).
        clock_applies_dst: Clock autonomously updates DST offset (Clock Capabilities bit 0).
        clock_manages_tz: Clock autonomously updates TZ offset (Clock Capabilities bit 1).

    """

    flags: ElapsedTimeFlags
    time_value: int
    time_resolution: TimeResolution
    is_tick_counter: bool
    is_utc: bool
    tz_dst_used: bool
    is_current_timeline: bool
    sync_source_type: TimeSource
    tz_dst_offset: int
    clock_needs_set: bool = False
    clock_applies_dst: bool = False
    clock_manages_tz: bool = False


class ElapsedTimeCharacteristic(BaseCharacteristic[ElapsedTimeData]):
    """Elapsed Time characteristic (0x2BF2).

    Reports the current time of a clock or tick counter.

    Read/indicate format: 11 bytes (9-byte Elapsed Time struct + Clock Status
    + Clock Capabilities).  Write format: 9 bytes (Elapsed Time struct only).
    """

    expected_type = ElapsedTimeData
    min_length: int = 9
    max_length: int = 11

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ElapsedTimeData:
        """Parse Current Elapsed Time from raw BLE bytes.

        Args:
            data: Raw bytearray (9 bytes for write echo, 11 bytes for read/indicate).
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            ElapsedTimeData with parsed time information.

        """
        flags_raw = data[0]
        flags = ElapsedTimeFlags(flags_raw & 0x33)  # Mask out resolution bits + reserved

        time_resolution = TimeResolution((flags_raw & _TIME_RESOLUTION_MASK) >> _TIME_RESOLUTION_SHIFT)

        time_value = DataParser.parse_int48(data, 1, signed=False)
        sync_source_type = TimeSource(data[7])
        tz_dst_offset = DataParser.parse_int8(data, 8, signed=True)

        clock_needs_set = False
        clock_applies_dst = False
        clock_manages_tz = False
        if len(data) >= _READ_LENGTH:
            clock_status = data[9]
            clock_needs_set = bool(clock_status & 0x01)
            clock_caps = data[10]
            clock_applies_dst = bool(clock_caps & 0x01)
            clock_manages_tz = bool(clock_caps & 0x02)

        return ElapsedTimeData(
            flags=flags,
            time_value=time_value,
            time_resolution=time_resolution,
            is_tick_counter=bool(flags & ElapsedTimeFlags.TICK_COUNTER),
            is_utc=bool(flags & ElapsedTimeFlags.UTC),
            tz_dst_used=bool(flags & ElapsedTimeFlags.TZ_DST_USED),
            is_current_timeline=bool(flags & ElapsedTimeFlags.CURRENT_TIMELINE),
            sync_source_type=sync_source_type,
            tz_dst_offset=tz_dst_offset,
            clock_needs_set=clock_needs_set,
            clock_applies_dst=clock_applies_dst,
            clock_manages_tz=clock_manages_tz,
        )

    def _encode_value(self, data: ElapsedTimeData) -> bytearray:
        """Encode ElapsedTimeData back to BLE bytes.

        Produces the full 11-byte read/indicate format including Clock Status
        and Clock Capabilities.

        Args:
            data: ElapsedTimeData instance.

        Returns:
            Encoded bytearray (11 bytes).

        """
        flags_raw = int(data.flags) | (data.time_resolution << _TIME_RESOLUTION_SHIFT)
        result = bytearray([flags_raw])
        result.extend(DataParser.encode_int48(data.time_value, signed=False))
        result.append(int(data.sync_source_type))
        result.extend(DataParser.encode_int8(data.tz_dst_offset, signed=True))

        clock_status = int(data.clock_needs_set)
        result.append(clock_status)

        clock_caps = int(data.clock_applies_dst) | (int(data.clock_manages_tz) << 1)
        result.append(clock_caps)

        return result
