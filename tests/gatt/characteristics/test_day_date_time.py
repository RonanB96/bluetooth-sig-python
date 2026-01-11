"""Tests for Day Date Time characteristic (0x2A0A)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import DayDateTimeCharacteristic, DayDateTimeData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDayDateTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for Day Date Time characteristic."""

    @pytest.fixture
    def characteristic(self) -> DayDateTimeCharacteristic:
        """Return a Day Date Time characteristic instance."""
        return DayDateTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Day Date Time characteristic."""
        return "2A0A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for day date time."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE3, 0x07, 12, 25, 10, 30, 45, 3]),
                expected_value=DayDateTimeData(dt=datetime(2019, 12, 25, 10, 30, 45), day_of_week=3),
                description="Wednesday, Christmas 2019",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE7, 0x07, 6, 15, 14, 30, 0, 4]),
                expected_value=DayDateTimeData(dt=datetime(2023, 6, 15, 14, 30, 0), day_of_week=4),
                description="Thursday, June 2023",
            ),
        ]

    def test_decode_with_day_of_week(self) -> None:
        """Test decoding date/time with day of week."""
        char = DayDateTimeCharacteristic()
        result = char.parse_value(bytearray([0xE3, 0x07, 12, 25, 10, 30, 45, 3]))
        assert result.dt == datetime(2019, 12, 25, 10, 30, 45)
        assert result.day_of_week == 3  # Wednesday

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = DayDateTimeCharacteristic()
        original = DayDateTimeData(dt=datetime(2023, 6, 15, 14, 30, 0), day_of_week=4)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
