"""Tests for CGM Session Start Time characteristic (0x2AAA)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.cgm_session_start_time import (
    CGMSessionStartTimeCharacteristic,
    CGMSessionStartTimeData,
)
from bluetooth_sig.gatt.characteristics.dst_offset import DSTOffset
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCGMSessionStartTimeCharacteristic(CommonCharacteristicTests):
    """Test CGM Session Start Time characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return CGMSessionStartTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2AAA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xE0,
                        0x07,  # year: 2016
                        0x06,  # month: June
                        0x0F,  # day: 15
                        0x0A,  # hour: 10
                        0x1E,  # minute: 30
                        0x00,  # second: 0
                        0x04,  # timezone: UTC+1 (4 * 15min = 60min)
                        0x04,  # dst_offset: 4 (daylight time +1h)
                    ]
                ),
                expected_value=CGMSessionStartTimeData(
                    start_time=datetime(2016, 6, 15, 10, 30, 0),
                    time_zone=4,
                    dst_offset=DSTOffset.DAYLIGHT_TIME,
                ),
                description="Typical session start, no CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xEA,
                        0x07,  # year: 2026
                        0x02,  # month: February
                        0x17,  # day: 23
                        0x08,  # hour: 8
                        0x00,  # minute: 0
                        0x00,  # second: 0
                        0x00,  # timezone: UTC
                        0x00,  # dst_offset: 0 (standard time)
                        0xAB,
                        0xCD,  # e2e_crc: 0xCDAB
                    ]
                ),
                expected_value=CGMSessionStartTimeData(
                    start_time=datetime(2026, 2, 23, 8, 0, 0),
                    time_zone=0,
                    dst_offset=DSTOffset.STANDARD_TIME,
                    e2e_crc=0xCDAB,
                ),
                description="Session start with CRC",
            ),
        ]

    def test_round_trip_without_crc(self) -> None:
        """Test encode/decode round-trip without CRC."""
        char = CGMSessionStartTimeCharacteristic()
        original = CGMSessionStartTimeData(
            start_time=datetime(2025, 12, 25, 14, 30, 45),
            time_zone=8,
            dst_offset=DSTOffset.STANDARD_TIME,
        )
        encoded = char.build_value(original)
        assert len(encoded) == 9
        decoded = char.parse_value(encoded)
        assert decoded.start_time == original.start_time
        assert decoded.time_zone == original.time_zone
        assert decoded.dst_offset == original.dst_offset
        assert decoded.e2e_crc is None

    def test_round_trip_with_crc(self) -> None:
        """Test encode/decode round-trip with CRC."""
        char = CGMSessionStartTimeCharacteristic()
        original = CGMSessionStartTimeData(
            start_time=datetime(2020, 1, 1, 0, 0, 0),
            time_zone=0,
            dst_offset=DSTOffset.STANDARD_TIME,
            e2e_crc=0x1234,
        )
        encoded = char.build_value(original)
        assert len(encoded) == 11
        decoded = char.parse_value(encoded)
        assert decoded.start_time == original.start_time
        assert decoded.e2e_crc == 0x1234
