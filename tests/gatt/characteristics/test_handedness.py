"""Tests for Handedness characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Handedness, HandednessCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHandednessCharacteristic(CommonCharacteristicTests):
    """Test suite for Handedness characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds handedness-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HandednessCharacteristic:
        """Return a Handedness characteristic instance."""
        return HandednessCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Handedness characteristic."""
        return "2B4A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for handedness."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]), expected_value=Handedness.LEFT_HANDED, description="Left handed"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]), expected_value=Handedness.RIGHT_HANDED, description="Right handed"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]), expected_value=Handedness.AMBIDEXTROUS, description="Ambidextrous"
            ),
        ]

    # === Handedness-Specific Tests ===

    @pytest.mark.parametrize(
        "handedness_value,expected_enum,description",
        [
            (0x00, Handedness.LEFT_HANDED, "Left handed"),
            (0x01, Handedness.RIGHT_HANDED, "Right handed"),
            (0x02, Handedness.AMBIDEXTROUS, "Ambidextrous"),
            (0x03, Handedness.UNSPECIFIED, "Unspecified"),
        ],
    )
    def test_handedness_values(
        self,
        characteristic: HandednessCharacteristic,
        handedness_value: int,
        expected_enum: Handedness,
        description: str,
    ) -> None:
        """Test handedness with various valid values."""
        data = bytearray([handedness_value])
        result = characteristic.parse_value(data)
        assert result == expected_enum

    def test_handedness_boundary_values(self, characteristic: HandednessCharacteristic) -> None:
        """Test handedness boundary values."""
        # Test left handed (0x00)
        result = characteristic.parse_value(bytearray([0x00]))
        assert result == Handedness.LEFT_HANDED

        # Test right handed (0x01)
        result = characteristic.parse_value(bytearray([0x01]))
        assert result == Handedness.RIGHT_HANDED

        # Test ambidextrous (0x02)
        result = characteristic.parse_value(bytearray([0x02]))
        assert result == Handedness.AMBIDEXTROUS

        # Test unspecified (0x03)
        result = characteristic.parse_value(bytearray([0x03]))
        assert result == Handedness.UNSPECIFIED

    def test_handedness_invalid_values(self, characteristic: HandednessCharacteristic) -> None:
        """Test handedness with invalid values."""
        # Test invalid value (0x04 is reserved)
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x04]))
        assert "Invalid Handedness: 4" in str(exc_info.value)

    def test_handedness_encoding(self, characteristic: HandednessCharacteristic) -> None:
        """Test encoding handedness back to bytes."""
        data = Handedness.RIGHT_HANDED
        result = characteristic.build_value(data)
        assert result == bytearray([0x01])
