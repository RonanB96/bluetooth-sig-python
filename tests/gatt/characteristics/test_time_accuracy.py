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
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Unknown accuracy"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="±1/8 second"),
            CharacteristicTestData(input_data=bytearray([128]), expected_value=128, description="±16 seconds"),
            CharacteristicTestData(input_data=bytearray([254]), expected_value=254, description="Out of range"),
        ]

    def test_unknown_accuracy(self) -> None:
        """Test unknown time accuracy."""
        char = TimeAccuracyCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0

    def test_precise_accuracy(self) -> None:
        """Test precise time accuracy (±1/8 second)."""
        char = TimeAccuracyCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == 1

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = TimeAccuracyCharacteristic()
        for value in [0, 1, 64, 128, 254]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
