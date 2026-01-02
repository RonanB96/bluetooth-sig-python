"""Tests for Correlated Color Temperature characteristic (0x2AED)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CorrelatedColorTemperatureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCorrelatedColorTemperatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Correlated Color Temperature characteristic."""

    @pytest.fixture
    def characteristic(self) -> CorrelatedColorTemperatureCharacteristic:
        """Return a Correlated Color Temperature characteristic instance."""
        return CorrelatedColorTemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Correlated Color Temperature characteristic."""
        return "2AE9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for correlated color temperature."""
        return [
            CharacteristicTestData(
                input_data=bytearray([32, 3]), expected_value=800, description="Minimum temperature (800K)"
            ),
            CharacteristicTestData(
                input_data=bytearray([168, 19]), expected_value=5032, description="Warm white (~5000K)"
            ),
            CharacteristicTestData(
                input_data=bytearray([254, 255]), expected_value=65534, description="Maximum temperature (65534K)"
            ),
        ]

    def test_warm_white(self) -> None:
        """Test warm white color temperature (~5000K)."""
        char = CorrelatedColorTemperatureCharacteristic()
        result = char.decode_value(bytearray([168, 19]))
        assert result == 5032

    def test_cool_white(self) -> None:
        """Test cool white color temperature (~6500K)."""
        char = CorrelatedColorTemperatureCharacteristic()
        # 6500K represented as uint16
        encoded = char.encode_value(6500)
        decoded = char.decode_value(encoded)
        assert decoded == 6500

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = CorrelatedColorTemperatureCharacteristic()
        for value in [800, 2700, 5000, 6500, 65534]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value
