"""Tests for Database Change Increment characteristic (0x2A99)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DatabaseChangeIncrementCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDatabaseChangeIncrementCharacteristic(CommonCharacteristicTests):
    """Test suite for Database Change Increment characteristic."""

    @pytest.fixture
    def characteristic(self) -> DatabaseChangeIncrementCharacteristic:
        """Return a Database Change Increment characteristic instance."""
        return DatabaseChangeIncrementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Database Change Increment characteristic."""
        return "2A99"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for database change increment."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0, 0, 0]), expected_value=0, description="No changes"),
            CharacteristicTestData(input_data=bytearray([1, 0, 0, 0]), expected_value=1, description="One change"),
            CharacteristicTestData(
                input_data=bytearray([255, 255, 255, 255]),
                expected_value=4294967295,
                description="Maximum changes",
            ),
        ]

    def test_no_changes(self) -> None:
        """Test zero database changes."""
        char = DatabaseChangeIncrementCharacteristic()
        result = char.parse_value(bytearray([0, 0, 0, 0]))
        assert result == 0

    def test_single_change(self) -> None:
        """Test single database change."""
        char = DatabaseChangeIncrementCharacteristic()
        result = char.parse_value(bytearray([1, 0, 0, 0]))
        assert result == 1

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = DatabaseChangeIncrementCharacteristic()
        for value in [0, 1, 1000, 4294967295]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
