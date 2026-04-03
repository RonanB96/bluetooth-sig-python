"""Tests for Current Elapsed Time characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.elapsed_time import (
    ElapsedTimeCharacteristic,
    ElapsedTimeData,
    ElapsedTimeFlags,
    TimeResolution,
)
from bluetooth_sig.gatt.characteristics.reference_time_information import TimeSource

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElapsedTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for ElapsedTimeCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> ElapsedTimeCharacteristic:
        return ElapsedTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x02\x40\x42\x0f\x00\x00\x00\x01\x00\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC,
                    time_value=1000000,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.NETWORK_TIME_PROTOCOL,
                    tz_dst_offset=0,
                ),
                description="UTC time, 1s resolution, NTP sync",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x05\xf4\x01\x00\x00\x00\x00\x00\x00\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.TICK_COUNTER,
                    time_value=500,
                    time_resolution=TimeResolution.HUNDRED_MILLISECONDS,
                    is_tick_counter=True,
                    is_utc=False,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                ),
                description="tick counter, 100ms resolution",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x30\x80\x51\x01\x00\x00\x00\x04\x08\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.TZ_DST_USED | ElapsedTimeFlags.CURRENT_TIMELINE,
                    time_value=86400,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=False,
                    tz_dst_used=True,
                    is_current_timeline=True,
                    sync_source_type=TimeSource.MANUAL,
                    tz_dst_offset=8,
                ),
                description="local time with TZ/DST offset +2h",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x12\x00\x00\x00\x00\x00\x00\x00\xec\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC | ElapsedTimeFlags.TZ_DST_USED,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=True,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=-20,
                ),
                description="UTC with negative TZ/DST offset -5h",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x08\x80\xee\x36\x00\x00\x00\x00\x00\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags(0),
                    time_value=3600000,
                    time_resolution=TimeResolution.ONE_MILLISECOND,
                    is_tick_counter=False,
                    is_utc=False,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                ),
                description="1ms resolution, one hour in ms",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x0c\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags(0),
                    time_value=1,
                    time_resolution=TimeResolution.HUNDRED_MICROSECONDS,
                    is_tick_counter=False,
                    is_utc=False,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                ),
                description="100µs resolution",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                    clock_needs_set=True,
                ),
                description="clock needs set",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                    clock_applies_dst=True,
                    clock_manages_tz=True,
                ),
                description="clock applies DST and manages TZ",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                ),
                description="UTC zero time",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01\x03"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=False,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=0,
                    clock_needs_set=True,
                    clock_applies_dst=True,
                    clock_manages_tz=True,
                ),
                description="all clock flags set",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x32\x80\x51\x01\x00\x00\x00\x04\x08\x01\x01"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC | ElapsedTimeFlags.TZ_DST_USED | ElapsedTimeFlags.CURRENT_TIMELINE,
                    time_value=86400,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=True,
                    is_current_timeline=True,
                    sync_source_type=TimeSource.MANUAL,
                    tz_dst_offset=8,
                    clock_needs_set=True,
                    clock_applies_dst=True,
                ),
                description="UTC + TZ/DST + current timeline, clock needs set + applies DST",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x12\x00\x00\x00\x00\x00\x00\x00\xec\x00\x02"),
                expected_value=ElapsedTimeData(
                    flags=ElapsedTimeFlags.UTC | ElapsedTimeFlags.TZ_DST_USED,
                    time_value=0,
                    time_resolution=TimeResolution.ONE_SECOND,
                    is_tick_counter=False,
                    is_utc=True,
                    tz_dst_used=True,
                    is_current_timeline=False,
                    sync_source_type=TimeSource.UNKNOWN,
                    tz_dst_offset=-20,
                    clock_manages_tz=True,
                ),
                description="UTC + TZ/DST offset -5h, clock manages TZ",
            ),
        ]
