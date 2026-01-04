"""Tests for Age characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AgeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAgeCharacteristic(CommonCharacteristicTests):
    """Test suite for Age characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds age-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> AgeCharacteristic:
        """Return an Age characteristic instance."""
        return AgeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Age characteristic."""
        return "2A80"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for age."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="0 years old"),
            CharacteristicTestData(input_data=bytearray([25]), expected_value=25, description="25 years old"),
            CharacteristicTestData(input_data=bytearray([50]), expected_value=50, description="50 years old"),
            CharacteristicTestData(input_data=bytearray([100]), expected_value=100, description="100 years old"),
        ]

    # === Age-Specific Tests ===

    @pytest.mark.parametrize(
        "age",
        [
            0,  # Newborn
            1,  # 1 year
            18,  # Adult
            65,  # Retirement age
            100,  # Century old
        ],
    )
    def test_age_various_values(self, characteristic: AgeCharacteristic, age: int) -> None:
        """Test age with various valid values."""
        data = bytearray([age])
        result = characteristic.parse_value(data)

        assert result == age

    def test_age_boundary_values(self, characteristic: AgeCharacteristic) -> None:
        """Test age boundary values (0 and 255)."""
        # Test 0 years
        result = characteristic.parse_value(bytearray([0]))

        assert result == 0

        # Test maximum age (255)
        result = characteristic.parse_value(bytearray([255]))

        assert result == 255
