"""Tests for Last Name characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LastNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLastNameCharacteristic(CommonCharacteristicTests):
    """Test suite for Last Name characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds last name-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> LastNameCharacteristic:
        """Return a Last Name characteristic instance."""
        return LastNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Last Name characteristic."""
        return "2A90"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for last name."""
        return [
            CharacteristicTestData(input_data=bytearray(b"Doe"), expected_value="Doe", description="Simple last name"),
            CharacteristicTestData(
                input_data=bytearray(b"Smith"), expected_value="Smith", description="Common last name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Johnson"), expected_value="Johnson", description="Longer last name"
            ),
        ]

    # === Last Name-Specific Tests ===

    @pytest.mark.parametrize(
        "last_name",
        [
            "Doe",
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
        ],
    )
    def test_last_name_values(self, characteristic: LastNameCharacteristic, last_name: str) -> None:
        """Test last name with various valid values."""
        data = bytearray(last_name.encode("utf-8"))
        result = characteristic.parse_value(data)
        assert result.value == last_name

    def test_last_name_empty(self, characteristic: LastNameCharacteristic) -> None:
        """Test empty last name."""
        result = characteristic.parse_value(bytearray())
        assert result.value == ""

    def test_last_name_unicode(self, characteristic: LastNameCharacteristic) -> None:
        """Test last name with unicode characters."""
        name = "Muñoz"
        data = bytearray(name.encode("utf-8"))
        result = characteristic.parse_value(data)
        assert result.value == name
