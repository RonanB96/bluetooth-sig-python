"""Tests for Temperature Type characteristic (0x2A1D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TemperatureTypeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperatureTypeCharacteristic(CommonCharacteristicTests):
    """Test suite for Temperature Type characteristic."""

    @pytest.fixture
    def characteristic(self) -> TemperatureTypeCharacteristic:
        """Return a Temperature Type characteristic instance."""
        return TemperatureTypeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Temperature Type characteristic."""
        return "2A1D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for temperature type."""
        return [
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Armpit"),
            CharacteristicTestData(input_data=bytearray([2]), expected_value=2, description="Body (general)"),
            CharacteristicTestData(input_data=bytearray([3]), expected_value=3, description="Ear"),
            CharacteristicTestData(input_data=bytearray([4]), expected_value=4, description="Finger"),
            CharacteristicTestData(input_data=bytearray([5]), expected_value=5, description="Gastro-intestinal Tract"),
            CharacteristicTestData(input_data=bytearray([6]), expected_value=6, description="Mouth"),
            CharacteristicTestData(input_data=bytearray([7]), expected_value=7, description="Rectum"),
            CharacteristicTestData(input_data=bytearray([8]), expected_value=8, description="Toe"),
            CharacteristicTestData(input_data=bytearray([9]), expected_value=9, description="Tympanum (ear drum)"),
        ]

    def test_armpit_type(self) -> None:
        """Test armpit temperature type."""
        char = TemperatureTypeCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result.value == 1

    def test_mouth_type(self) -> None:
        """Test mouth temperature type."""
        char = TemperatureTypeCharacteristic()
        result = char.parse_value(bytearray([6]))
        assert result.value == 6

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = TemperatureTypeCharacteristic()
        for temp_type in range(1, 10):
            encoded = char.build_value(temp_type)
            decoded = char.parse_value(encoded)
            assert decoded.value == temp_type
