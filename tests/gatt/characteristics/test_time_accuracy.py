"""Tests for Time Accuracy characteristic (0x2A12)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TimeAccuracyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeAccuracyCharacteristic(CommonCharacteristicTests):
    """Test suite for Time Accuracy characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeAccuracyCharacteristic:
        """Return a Time Accuracy characteristic instance."""
        return TimeAccuracyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Time Accuracy characteristic."""
        return "2A12"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for time accuracy."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0.0, description="Zero accuracy"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=0.125, description="±1/8 second"),
            CharacteristicTestData(input_data=bytearray([8]), expected_value=1.0, description="±1 second"),
            CharacteristicTestData(input_data=bytearray([128]), expected_value=16.0, description="±16 seconds"),
            CharacteristicTestData(input_data=bytearray([253]), expected_value=31.625, description="Max valid range"),
        ]

    def test_zero_accuracy(self) -> None:
        """Test zero time accuracy (0 seconds drift)."""
        char = TimeAccuracyCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0.0

    def test_precise_accuracy(self) -> None:
        """Test precise time accuracy (±1/8 second = 0.125s)."""
        char = TimeAccuracyCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == 0.125

    def test_max_valid_accuracy(self) -> None:
        """Test maximum valid time accuracy (253 * 0.125 = 31.625s)."""
        char = TimeAccuracyCharacteristic()
        result = char.parse_value(bytearray([253]))
        assert result == 31.625
