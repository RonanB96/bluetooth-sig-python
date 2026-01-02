"""Tests for Heart Rate Control Point characteristic (0x2A39)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HeartRateControlPointCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeartRateControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Heart Rate Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> HeartRateControlPointCharacteristic:
        """Return a Heart Rate Control Point characteristic instance."""
        return HeartRateControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Heart Rate Control Point characteristic."""
        return "2A39"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for heart rate control point."""
        return [
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Reset Energy Expended"),
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Reserved value"),
        ]

    def test_reset_energy_expended(self) -> None:
        """Test reset energy expended command."""
        char = HeartRateControlPointCharacteristic()
        result = char.decode_value(bytearray([1]))
        assert result == 1

    def test_encode_reset_command(self) -> None:
        """Test encoding reset command."""
        char = HeartRateControlPointCharacteristic()
        encoded = char.encode_value(1)
        assert encoded == bytearray([1])

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = HeartRateControlPointCharacteristic()
        encoded = char.encode_value(1)
        decoded = char.decode_value(encoded)
        assert decoded == 1
