"""Tests for Current Elapsed Time characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.current_elapsed_time import (
    CurrentElapsedTimeCharacteristic,
    CurrentElapsedTimeData,
    ElapsedTimeFlags,
    TimeResolution,
)
from bluetooth_sig.gatt.characteristics.reference_time_information import TimeSource


@pytest.fixture
def characteristic() -> CurrentElapsedTimeCharacteristic:
    """Create a CurrentElapsedTimeCharacteristic instance."""
    return CurrentElapsedTimeCharacteristic()


class TestCurrentElapsedTimeDecode:
    """Tests for Current Elapsed Time decoding."""

    def test_basic_utc_time(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding a UTC time-of-day value (1 second resolution)."""
        # Flags: UTC (bit 1) = 0x02, resolution 1s (bits 2-3 = 00)
        # Time: 1000000 = 0x0F4240 (as uint48 little-endian: 40 42 0F 00 00 00)
        # Sync source: 0x01
        # TZ/DST offset: 0 (sint8)
        data = bytearray(b"\x02\x40\x42\x0f\x00\x00\x00\x01\x00")
        result = characteristic.parse_value(data)
        assert isinstance(result, CurrentElapsedTimeData)
        assert result.is_utc is True
        assert result.is_tick_counter is False
        assert result.time_resolution == TimeResolution.ONE_SECOND
        assert result.time_value == 1000000
        assert result.sync_source_type == 1
        assert result.tz_dst_offset == 0

    def test_tick_counter_100ms(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding a tick counter with 100ms resolution."""
        # Flags: tick_counter (bit 0) + resolution 100ms (bits 2-3 = 01)
        #   = 0x01 | (0x01 << 2) = 0x01 | 0x04 = 0x05
        # Time: 500 = 0x01F4 (as uint48 LE: F4 01 00 00 00 00)
        # Sync source: 0x00
        # TZ/DST offset: 0
        data = bytearray(b"\x05\xf4\x01\x00\x00\x00\x00\x00\x00")
        result = characteristic.parse_value(data)
        assert result.is_tick_counter is True
        assert result.time_resolution == TimeResolution.HUNDRED_MILLISECONDS
        assert result.time_value == 500
        assert result.tz_dst_used is False

    def test_local_time_with_tz(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding local time with TZ/DST offset."""
        # Flags: tz_dst_used (bit 4) + current_timeline (bit 5) = 0x30
        # Time: 86400 = 0x015180 (one day in seconds)
        #   LE: 80 51 01 00 00 00
        # Sync source: 0x04
        # TZ/DST offset: 8 (= 2 hours ahead, sint8)
        data = bytearray(b"\x30\x80\x51\x01\x00\x00\x00\x04\x08")
        result = characteristic.parse_value(data)
        assert result.is_utc is False
        assert result.tz_dst_used is True
        assert result.is_current_timeline is True
        assert result.time_value == 86400
        assert result.tz_dst_offset == 8

    def test_negative_tz_offset(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding with negative TZ/DST offset."""
        # Flags: UTC + tz_dst_used = 0x02 | 0x10 = 0x12
        # Time value: zero, Sync source: 0x00
        # TZ/DST offset: -20 (= -5 hours, sint8 = 0xEC)
        data = bytearray(b"\x12\x00\x00\x00\x00\x00\x00\x00\xec")
        result = characteristic.parse_value(data)
        assert result.is_utc is True
        assert result.tz_dst_used is True
        assert result.tz_dst_offset == -20

    def test_1ms_resolution(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding with 1 millisecond resolution."""
        # Flags: resolution 1ms (bits 2-3 = 10) = 0x08
        # Time: 3600000 = 0x36EE80 (one hour in ms)
        #   LE: 80 EE 36 00 00 00
        data = bytearray(b"\x08\x80\xee\x36\x00\x00\x00\x00\x00")
        result = characteristic.parse_value(data)
        assert result.time_resolution == TimeResolution.ONE_MILLISECOND
        assert result.time_value == 3600000

    def test_100us_resolution(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test decoding with 100 microsecond resolution."""
        # Flags: resolution 100µs (bits 2-3 = 11) = 0x0C
        data = bytearray(b"\x0c\x01\x00\x00\x00\x00\x00\x00\x00")
        result = characteristic.parse_value(data)
        assert result.time_resolution == TimeResolution.HUNDRED_MICROSECONDS
        assert result.time_value == 1


class TestCurrentElapsedTimeEncode:
    """Tests for Current Elapsed Time encoding."""

    def test_encode_utc_time(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test encoding a UTC time value."""
        data = CurrentElapsedTimeData(
            flags=ElapsedTimeFlags.UTC,
            time_value=1000000,
            time_resolution=TimeResolution.ONE_SECOND,
            is_tick_counter=False,
            is_utc=True,
            tz_dst_used=False,
            is_current_timeline=False,
            sync_source_type=TimeSource.NETWORK_TIME_PROTOCOL,
            tz_dst_offset=0,
        )
        result = characteristic.build_value(data)
        assert result == bytearray(b"\x02\x40\x42\x0f\x00\x00\x00\x01\x00")

    def test_encode_tick_counter(self, characteristic: CurrentElapsedTimeCharacteristic) -> None:
        """Test encoding a tick counter with 100ms resolution."""
        data = CurrentElapsedTimeData(
            flags=ElapsedTimeFlags.TICK_COUNTER,
            time_value=500,
            time_resolution=TimeResolution.HUNDRED_MILLISECONDS,
            is_tick_counter=True,
            is_utc=False,
            tz_dst_used=False,
            is_current_timeline=False,
            sync_source_type=TimeSource.UNKNOWN,
            tz_dst_offset=0,
        )
        result = characteristic.build_value(data)
        assert result == bytearray(b"\x05\xf4\x01\x00\x00\x00\x00\x00\x00")


class TestCurrentElapsedTimeRoundTrip:
    """Round-trip tests for Current Elapsed Time."""

    @pytest.mark.parametrize(
        ("flags", "resolution", "time_val", "sync", "tz_dst"),
        [
            (ElapsedTimeFlags.UTC, TimeResolution.ONE_SECOND, 0, TimeSource.UNKNOWN, 0),
            (ElapsedTimeFlags.TICK_COUNTER, TimeResolution.HUNDRED_MILLISECONDS, 500, TimeSource.UNKNOWN, 0),
            (
                ElapsedTimeFlags.UTC | ElapsedTimeFlags.TZ_DST_USED | ElapsedTimeFlags.CURRENT_TIMELINE,
                TimeResolution.ONE_SECOND,
                86400,
                TimeSource.MANUAL,
                8,
            ),
            (
                ElapsedTimeFlags.UTC | ElapsedTimeFlags.TZ_DST_USED,
                TimeResolution.ONE_SECOND,
                0,
                TimeSource.UNKNOWN,
                -20,
            ),
        ],
    )
    def test_round_trip(
        self,
        characteristic: CurrentElapsedTimeCharacteristic,
        flags: ElapsedTimeFlags,
        resolution: TimeResolution,
        time_val: int,
        sync: TimeSource,
        tz_dst: int,
    ) -> None:
        """Test encode -> decode round-trip."""
        original = CurrentElapsedTimeData(
            flags=flags,
            time_value=time_val,
            time_resolution=resolution,
            is_tick_counter=bool(flags & ElapsedTimeFlags.TICK_COUNTER),
            is_utc=bool(flags & ElapsedTimeFlags.UTC),
            tz_dst_used=bool(flags & ElapsedTimeFlags.TZ_DST_USED),
            is_current_timeline=bool(flags & ElapsedTimeFlags.CURRENT_TIMELINE),
            sync_source_type=sync,
            tz_dst_offset=tz_dst,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
