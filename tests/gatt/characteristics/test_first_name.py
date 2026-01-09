"""Tests for First Name characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import FirstNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFirstNameCharacteristic(CommonCharacteristicTests):
    """Test suite for First Name characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds first name-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> FirstNameCharacteristic:
        """Return a First Name characteristic instance."""
        return FirstNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for First Name characteristic."""
        return "2A8A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for first name."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"John"), expected_value="John", description="Simple first name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Jane"), expected_value="Jane", description="Another first name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Alex"), expected_value="Alex", description="Short first name"
            ),
        ]

    # === First Name-Specific Tests ===

    @pytest.mark.parametrize(
        "first_name",
        [
            "John",
            "Jane",
            "Michael",
            "Sarah",
            "David",
        ],
    )
    def test_first_name_values(self, characteristic: FirstNameCharacteristic, first_name: str) -> None:
        """Test first name with various valid values."""
        data = bytearray(first_name.encode("utf-8"))
        result = characteristic.parse_value(data)
        assert result == first_name

    def test_first_name_empty(self, characteristic: FirstNameCharacteristic) -> None:
        """Test empty first name."""
        result = characteristic.parse_value(bytearray())
        assert result == ""

    def test_first_name_unicode(self, characteristic: FirstNameCharacteristic) -> None:
        """Test first name with unicode characters."""
        name = "José"
        data = bytearray(name.encode("utf-8"))
        result = characteristic.parse_value(data)
        assert result == name
