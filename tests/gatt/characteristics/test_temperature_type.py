"""Tests for Temperature Type characteristic (0x2A1D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TemperatureTypeCharacteristic
from bluetooth_sig.gatt.characteristics.temperature_type import TemperatureType
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
            CharacteristicTestData(
                input_data=bytearray([1]), expected_value=TemperatureType.ARMPIT, description="Armpit"
            ),
            CharacteristicTestData(
                input_data=bytearray([2]), expected_value=TemperatureType.BODY_GENERAL, description="Body (general)"
            ),
            CharacteristicTestData(input_data=bytearray([3]), expected_value=TemperatureType.EAR, description="Ear"),
            CharacteristicTestData(
                input_data=bytearray([4]), expected_value=TemperatureType.FINGER, description="Finger"
            ),
            CharacteristicTestData(
                input_data=bytearray([5]),
                expected_value=TemperatureType.GASTROINTESTINAL_TRACT,
                description="Gastro-intestinal Tract",
            ),
            CharacteristicTestData(
                input_data=bytearray([6]), expected_value=TemperatureType.MOUTH, description="Mouth"
            ),
            CharacteristicTestData(
                input_data=bytearray([7]), expected_value=TemperatureType.RECTUM, description="Rectum"
            ),
            CharacteristicTestData(input_data=bytearray([8]), expected_value=TemperatureType.TOE, description="Toe"),
            CharacteristicTestData(
                input_data=bytearray([9]), expected_value=TemperatureType.TYMPANUM, description="Tympanum (ear drum)"
            ),
        ]

    def test_armpit_type(self) -> None:
        """Test armpit temperature type."""
        char = TemperatureTypeCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == TemperatureType.ARMPIT

    def test_mouth_type(self) -> None:
        """Test mouth temperature type."""
        char = TemperatureTypeCharacteristic()
        result = char.parse_value(bytearray([6]))
        assert result == TemperatureType.MOUTH

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = TemperatureTypeCharacteristic()
        for temp_type in TemperatureType:
            if temp_type is TemperatureType.RESERVED_0:
                continue
            encoded = char.build_value(temp_type)
            decoded = char.parse_value(encoded)
            assert decoded == temp_type
