"""Tests for Date Time characteristic (0x2A08)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import DateTimeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDateTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for Date Time characteristic."""

    @pytest.fixture
    def characteristic(self) -> DateTimeCharacteristic:
        """Return a Date Time characteristic instance."""
        return DateTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Date Time characteristic."""
        return "2A08"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for date time."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE3, 0x07, 12, 25, 10, 30, 45]),
                expected_value=datetime(2019, 12, 25, 10, 30, 45),
                description="Christmas 2019",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE4, 0x07, 1, 1, 0, 0, 0]),
                expected_value=datetime(2020, 1, 1, 0, 0, 0),
                description="New Year 2020",
            ),
        ]

    def test_decode_christmas_2019(self) -> None:
        """Test decoding Christmas 2019 date/time."""
        char = DateTimeCharacteristic()
        result = char.parse_value(bytearray([0xE3, 0x07, 12, 25, 10, 30, 45]))
        assert result == datetime(2019, 12, 25, 10, 30, 45)

    def test_decode_new_year_2020(self) -> None:
        """Test decoding New Year 2020 date/time."""
        char = DateTimeCharacteristic()
        result = char.parse_value(bytearray([0xE4, 0x07, 1, 1, 0, 0, 0]))
        assert result == datetime(2020, 1, 1, 0, 0, 0)

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve datetime."""
        char = DateTimeCharacteristic()
        original = datetime(2023, 6, 15, 14, 30, 0)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
