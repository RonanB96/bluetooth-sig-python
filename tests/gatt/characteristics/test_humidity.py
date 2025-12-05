"""Tests for Humidity characteristic (0x2A6F)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHumidityCharacteristic(CommonCharacteristicTests):
    """Test Humidity characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> HumidityCharacteristic:
        """Provide Humidity characteristic for testing."""
        return HumidityCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Humidity characteristic."""
        return "2A6F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid humidity test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x88, 0x13]), expected_value=50.0, description="50.00% humidity"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x58, 0x1B]), expected_value=70.0, description="70.00% humidity"
            ),
        ]

    # === Humidity-Specific Tests ===
    def test_humidity_precision_and_range(self, characteristic: HumidityCharacteristic) -> None:
        """Test humidity precision and valid range boundaries."""
        # Test 0% humidity (boundary)
        result = characteristic.decode_value(bytearray([0x00, 0x00]))
        assert result == 0.0

        # Test 100% humidity (boundary)
        result = characteristic.decode_value(bytearray([0x10, 0x27]))  # 10000 = 100.00%
        assert result is not None
        assert abs(result - 100.0) < 0.01

        # Test precision (50.00%)
        result = characteristic.decode_value(bytearray([0x88, 0x13]))  # 5000 = 50.00%
        assert result is not None
        assert abs(result - 50.0) < 0.01

    def test_humidity_out_of_range_validation(self, characteristic: HumidityCharacteristic) -> None:
        """Test that special value 0xFFFF returns None."""
        # Test special value 0xFFFF should return None (value is not known)
        result = characteristic.decode_value(bytearray([0xFF, 0xFF]))
        assert result is None

    def test_humidity_encoding_accuracy(self, characteristic: HumidityCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding typical values
        assert characteristic.encode_value(50.0) == bytearray([0x88, 0x13])
        assert characteristic.encode_value(0.0) == bytearray([0x00, 0x00])
        assert characteristic.encode_value(100.0) == bytearray([0x10, 0x27])

    def test_raw_decode_without_validation(self, characteristic: HumidityCharacteristic) -> None:
        """Test raw decode_value method works for normal values."""
        # Test normal value
        data = bytearray([0x88, 0x13])  # 5000 = 50.00%
        result = characteristic.decode_value(data)
        assert result is not None
        assert abs(result - 50.0) < 0.01

    def test_characteristic_metadata(self, characteristic: HumidityCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Humidity"
        assert characteristic.unit == "%"
        assert characteristic.uuid == "2A6F"

    def test_humidity_precision(self, characteristic: HumidityCharacteristic) -> None:
        """Test humidity precision (0.01% resolution)."""
        # Test precision
        data = bytearray([0x01, 0x00])  # 1 = 0.01%
        result = characteristic.decode_value(data)
        assert result == 0.01

        data = bytearray([0x0A, 0x00])  # 10 = 0.10%
        result = characteristic.decode_value(data)
        assert result == 0.10
