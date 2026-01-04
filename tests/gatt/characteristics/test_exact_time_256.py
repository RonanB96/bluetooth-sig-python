"""Tests for Exact Time 256 characteristic (0x2A0C)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import ExactTime256Characteristic, ExactTime256Data
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestExactTime256Characteristic(CommonCharacteristicTests):
    """Test suite for Exact Time 256 characteristic."""

    @pytest.fixture
    def characteristic(self) -> ExactTime256Characteristic:
        """Return an Exact Time 256 characteristic instance."""
        return ExactTime256Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Exact Time 256 characteristic."""
        return "2A0C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for exact time 256."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE3, 0x07, 12, 25, 10, 30, 45, 3, 128]),
                expected_value=ExactTime256Data(dt=datetime(2019, 12, 25, 10, 30, 45), day_of_week=3, fractions256=128),
                description="Christmas 2019 with fractions",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE7, 0x07, 6, 15, 14, 30, 0, 4, 64]),
                expected_value=ExactTime256Data(dt=datetime(2023, 6, 15, 14, 30, 0), day_of_week=4, fractions256=64),
                description="Thursday, June 2023 with fractions",
            ),
        ]

    def test_decode_with_fractions(self) -> None:
        """Test decoding exact time with 1/256 second fractions."""
        char = ExactTime256Characteristic()
        result = char.parse_value(bytearray([0xE3, 0x07, 12, 25, 10, 30, 45, 3, 128]))
        assert result.value.dt == datetime(2019, 12, 25, 10, 30, 45)
        assert result.value.day_of_week == 3
        assert result.value.fractions256 == 128  # 128/256 = 0.5 seconds

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = ExactTime256Characteristic()
        original = ExactTime256Data(dt=datetime(2023, 6, 15, 14, 30, 0), day_of_week=4, fractions256=64)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.value == original
