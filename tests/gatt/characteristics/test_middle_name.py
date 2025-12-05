"""Tests for Middle Name characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MiddleNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMiddleNameCharacteristic(CommonCharacteristicTests):
    """Test suite for Middle Name characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds middle name-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> MiddleNameCharacteristic:
        """Return a Middle Name characteristic instance."""
        return MiddleNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Middle Name characteristic."""
        return "2B48"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for middle name."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"James"), expected_value="James", description="Simple middle name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Marie"), expected_value="Marie", description="Another middle name"
            ),
            CharacteristicTestData(input_data=bytearray(b"Lee"), expected_value="Lee", description="Short middle name"),
        ]

    # === Middle Name-Specific Tests ===

    @pytest.mark.parametrize(
        "middle_name",
        [
            "James",
            "Marie",
            "Lee",
            "Alexander",
            "Rose",
        ],
    )
    def test_middle_name_values(self, characteristic: MiddleNameCharacteristic, middle_name: str) -> None:
        """Test middle name with various valid values."""
        data = bytearray(middle_name.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == middle_name

    def test_middle_name_empty(self, characteristic: MiddleNameCharacteristic) -> None:
        """Test empty middle name."""
        result = characteristic.decode_value(bytearray())
        assert result == ""

    def test_middle_name_unicode(self, characteristic: MiddleNameCharacteristic) -> None:
        """Test middle name with unicode characters."""
        name = "José"
        data = bytearray(name.encode("utf-8"))
        result = characteristic.decode_value(data)
        assert result == name
