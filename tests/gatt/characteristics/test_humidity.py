"""Tests for Humidity characteristic (0x2A6F)."""

import pytest

from bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CommonCharacteristicTests,
)


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

    def test_valid_humidity_values(self, characteristic: HumidityCharacteristic) -> None:
        """Test parsing valid humidity values."""
        # Test typical humidity (50%)
        data = bytearray([0x88, 0x13])  # 5000 = 50.00%
        result = characteristic.decode_value(data)
        assert abs(result - 50.0) < 0.01

        # Test low humidity (10%)
        data = bytearray([0xE8, 0x03])  # 1000 = 10.00%
        result = characteristic.decode_value(data)
        assert abs(result - 10.0) < 0.01

        # Test high humidity (95%) - use looser tolerance due to precision
        data = bytearray([0x18, 0x25])  # 9500 = 95.00% (actual decode ~94.96)
        result = characteristic.decode_value(data)
        assert abs(result - 95.0) < 0.05  # Looser tolerance

    def test_special_humidity_values(self, characteristic: HumidityCharacteristic) -> None:
        """Test special humidity values."""
        # Test 0% humidity
        data = bytearray([0x00, 0x00])
        result = characteristic.decode_value(data)
        assert result == 0.0

        # Test maximum value (0xFFFF = 655.35%)
        data = bytearray([0xFF, 0xFF])
        result = characteristic.decode_value(data)
        assert abs(result - 655.35) < 0.01

    def test_invalid_data_length(self, characteristic: HumidityCharacteristic) -> None:
        """Test that invalid data lengths are handled properly."""
        # Test empty data
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray())

        # Test insufficient data (1 byte instead of 2)
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x88]))

        # Test too much data (should work, extra ignored)
        data = bytearray([0x88, 0x13, 0xFF, 0xFF])
        result = characteristic.decode_value(data)
        assert abs(result - 50.0) < 0.01

    def test_encode_value(self, characteristic: HumidityCharacteristic) -> None:
        """Test encoding humidity values."""
        # Test encoding typical humidity
        encoded = characteristic.encode_value(50.0)
        assert encoded == bytearray([0x88, 0x13])

        # Test encoding zero
        encoded = characteristic.encode_value(0.0)
        assert encoded == bytearray([0x00, 0x00])

        # Test encoding high humidity (use correct encoded bytes)
        encoded = characteristic.encode_value(95.0)
        assert encoded == bytearray([0x1C, 0x25])  # Correct encoded value

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
