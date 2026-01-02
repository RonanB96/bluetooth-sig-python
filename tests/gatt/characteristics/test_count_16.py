"""Tests for Count 16 characteristic (0x2AEA)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Count16Characteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCount16Characteristic(CommonCharacteristicTests):
    """Test suite for Count 16 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Count16Characteristic:
        """Return a Count 16 characteristic instance."""
        return Count16Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Count 16 characteristic."""
        return "2AEA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for count 16."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0, description="Zero count"),
            CharacteristicTestData(input_data=bytearray([1, 0]), expected_value=1, description="Count of 1"),
            CharacteristicTestData(
                input_data=bytearray([254, 255]), expected_value=65534, description="High count value"
            ),
        ]

    def test_zero_count(self) -> None:
        """Test zero count."""
        char = Count16Characteristic()
        result = char.decode_value(bytearray([0, 0]))
        assert result == 0

    def test_maximum_count(self) -> None:
        """Test maximum count value."""
        char = Count16Characteristic()
        result = char.decode_value(bytearray([255, 255]))
        assert result == 65535

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = Count16Characteristic()
        for value in [0, 1, 100, 32768, 65534]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value
