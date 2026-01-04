"""Tests for Count 24 characteristic (0x2AEC)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Count24Characteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCount24Characteristic(CommonCharacteristicTests):
    """Test suite for Count 24 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Count24Characteristic:
        """Return a Count 24 characteristic instance."""
        return Count24Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Count 24 characteristic."""
        return "2AEB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for count 24."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0, 0]), expected_value=0, description="Zero count"),
            CharacteristicTestData(input_data=bytearray([1, 0, 0]), expected_value=1, description="Count of 1"),
            CharacteristicTestData(
                input_data=bytearray([254, 255, 255]),
                expected_value=16777214,
                description="High count value",
            ),
        ]

    def test_zero_count(self) -> None:
        """Test zero count."""
        char = Count24Characteristic()
        result = char.parse_value(bytearray([0, 0, 0]))
        assert result == 0

    def test_maximum_count(self) -> None:
        """Test maximum count value."""
        char = Count24Characteristic()
        result = char.parse_value(bytearray([255, 255, 255]))
        # 16777215 is a special value meaning "not known"

        assert result.raw_int == 16777215

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = Count24Characteristic()
        for value in [0, 1, 100, 65536, 16777214]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
