"""Tests for Gust Factor characteristic (0x2A74)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GustFactorCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGustFactorCharacteristic(CommonCharacteristicTests):
    """Test suite for Gust Factor characteristic."""

    @pytest.fixture
    def characteristic(self) -> GustFactorCharacteristic:
        """Return a Gust Factor characteristic instance."""
        return GustFactorCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Gust Factor characteristic."""
        return "2A74"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for gust factor."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0.0, description="No gust"),
            CharacteristicTestData(
                input_data=bytearray([100]), expected_value=10.0, description="Moderate gust (10.0)"
            ),
            CharacteristicTestData(input_data=bytearray([255]), expected_value=25.5, description="Maximum gust (25.5)"),
        ]

    def test_no_gust(self) -> None:
        """Test no gust factor."""
        char = GustFactorCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0.0

    def test_moderate_gust(self) -> None:
        """Test moderate gust factor (10.0)."""
        char = GustFactorCharacteristic()
        result = char.parse_value(bytearray([100]))
        assert result == 10.0

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = GustFactorCharacteristic()
        for value in [0.0, 5.0, 15.0, 25.5]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
