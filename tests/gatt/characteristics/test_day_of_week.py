"""Tests for Day of Week characteristic (0x2A09)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DayOfWeekCharacteristic
from bluetooth_sig.types.gatt_enums import DayOfWeek
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDayOfWeekCharacteristic(CommonCharacteristicTests):
    """Test suite for Day of Week characteristic."""

    @pytest.fixture
    def characteristic(self) -> DayOfWeekCharacteristic:
        """Return a Day of Week characteristic instance."""
        return DayOfWeekCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Day of Week characteristic."""
        return "2A09"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for day of week."""
        return [
            CharacteristicTestData(input_data=bytearray([1]), expected_value=DayOfWeek.MONDAY, description="Monday"),
            CharacteristicTestData(input_data=bytearray([5]), expected_value=DayOfWeek.FRIDAY, description="Friday"),
            CharacteristicTestData(input_data=bytearray([7]), expected_value=DayOfWeek.SUNDAY, description="Sunday"),
        ]

    def test_monday(self) -> None:
        """Test Monday (day 1)."""
        char = DayOfWeekCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == DayOfWeek.MONDAY

    def test_sunday(self) -> None:
        """Test Sunday (day 7)."""
        char = DayOfWeekCharacteristic()
        result = char.parse_value(bytearray([7]))
        assert result == DayOfWeek.SUNDAY

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = DayOfWeekCharacteristic()
        for day in DayOfWeek:
            if day is DayOfWeek.UNKNOWN:
                continue
            encoded = char.build_value(day)
            decoded = char.parse_value(encoded)
            assert decoded == day
