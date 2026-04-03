"""Tests for User Index characteristic (0x2A9A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import UserIndexCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUserIndexCharacteristic(CommonCharacteristicTests):
    """Test suite for User Index characteristic."""

    @pytest.fixture
    def characteristic(self) -> UserIndexCharacteristic:
        """Return a User Index characteristic instance."""
        return UserIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for User Index characteristic."""
        return "2A9A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for user index."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Unknown user"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="User 1"),
            CharacteristicTestData(input_data=bytearray([5]), expected_value=5, description="User 5"),
            CharacteristicTestData(input_data=bytearray([10]), expected_value=10, description="User 10"),
            CharacteristicTestData(input_data=bytearray([100]), expected_value=100, description="User 100"),
            CharacteristicTestData(input_data=bytearray([255]), expected_value=255, description="User 255"),
        ]

    def test_unknown_user(self) -> None:
        """Test unknown user index."""
        char = UserIndexCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0

    def test_first_user(self) -> None:
        """Test first user index."""
        char = UserIndexCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == 1
