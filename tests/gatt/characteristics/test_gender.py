"""Tests for Gender characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Gender, GenderCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGenderCharacteristic(CommonCharacteristicTests):
    """Test suite for Gender characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds gender-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> GenderCharacteristic:
        """Return a Gender characteristic instance."""
        return GenderCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Gender characteristic."""
        return "2A8C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for gender."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=Gender.MALE, description="Male"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=Gender.FEMALE, description="Female"),
            CharacteristicTestData(
                input_data=bytearray([2]), expected_value=Gender.UNSPECIFIED, description="Unspecified"
            ),
        ]

    # === Gender-Specific Tests ===

    @pytest.mark.parametrize(
        "gender_code,expected_enum,gender_name",
        [
            (0, Gender.MALE, "Male"),
            (1, Gender.FEMALE, "Female"),
            (2, Gender.UNSPECIFIED, "Unspecified"),
        ],
    )
    def test_gender_values(
        self, characteristic: GenderCharacteristic, gender_code: int, expected_enum: Gender, gender_name: str
    ) -> None:
        """Test gender with various valid values."""
        data = bytearray([gender_code])
        result = characteristic.parse_value(data)
        assert result == expected_enum

    def test_gender_boundary_values(self, characteristic: GenderCharacteristic) -> None:
        """Test gender boundary values."""
        # Test male (0)
        result = characteristic.parse_value(bytearray([0]))
        assert result == Gender.MALE

        # Test female (1)
        result = characteristic.parse_value(bytearray([1]))
        assert result == Gender.FEMALE

        # Test unspecified (2)
        result = characteristic.parse_value(bytearray([2]))
        assert result == Gender.UNSPECIFIED

    def test_gender_invalid_values(self, characteristic: GenderCharacteristic) -> None:
        """Test gender with invalid values."""
        # Test invalid value (3 is reserved)
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([3]))
        assert "Invalid Gender: 3 (expected range [0, 2])" in str(exc_info.value)

    def test_gender_encoding(self, characteristic: GenderCharacteristic) -> None:
        """Test encoding gender back to bytes."""
        data = Gender.FEMALE
        result = characteristic.build_value(data)
        assert result == bytearray([1])
