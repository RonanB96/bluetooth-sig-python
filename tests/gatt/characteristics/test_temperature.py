"""Tests for Temperature characteristic (0x2A6E)."""

import pytest

from bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic
from bluetooth_sig.gatt.constants import SINT16_MAX, SINT16_MIN
from tests.gatt.characteristics.test_characteristic_common import (
    CommonCharacteristicTests,
)


class TestTemperatureCharacteristic(CommonCharacteristicTests):
    """Test Temperature characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> TemperatureCharacteristic:
        """Provide Temperature characteristic for testing."""
        return TemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Temperature characteristic."""
        return "2A6E"

    def test_valid_temperature_values(self, characteristic: TemperatureCharacteristic) -> None:
        """Test parsing valid temperature values."""
        # Test typical room temperature (22°C)
        data = bytearray([0x64, 0x08])  # 2148 = 21.48°C
        result = characteristic.decode_value(data)
        assert abs(result - 21.48) < 0.01

        # Test freezing point (0°C)
        data = bytearray([0x00, 0x00])
        result = characteristic.decode_value(data)
        assert result == 0.0

        # Test negative temperature (-10°C)
        data = bytearray([0x18, 0xFC])  # -1000 = -10.00°C
        result = characteristic.decode_value(data)
        assert abs(result + 10.0) < 0.01

    def test_extreme_temperature_values(self, characteristic: TemperatureCharacteristic) -> None:
        """Test parsing extreme temperature values."""
        # Test maximum positive value (using proper constants)
        data = bytearray([SINT16_MAX & 0xFF, (SINT16_MAX >> 8) & 0xFF])  # 32767 = 327.67°C
        result = characteristic.decode_value(data)
        assert abs(result - 327.67) < 0.01

        # Test maximum negative value (using proper constants)
        data = bytearray([SINT16_MIN & 0xFF, (SINT16_MIN >> 8) & 0xFF])  # -32768 = -327.68°C
        result = characteristic.decode_value(data)
        assert abs(result + 327.68) < 0.01

    def test_invalid_data_length(self, characteristic: TemperatureCharacteristic) -> None:
        """Test that invalid data lengths are handled properly."""
        # Test empty data (expects ValueError, not InsufficientDataError)
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray())

        # Test insufficient data (1 byte instead of 2)
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x64]))

        # Test too much data (should work, extra ignored)
        data = bytearray([0x64, 0x08, 0xFF, 0xFF])
        result = characteristic.decode_value(data)
        assert abs(result - 21.48) < 0.01

    def test_encode_value(self, characteristic: TemperatureCharacteristic) -> None:
        """Test encoding temperature values."""
        # Test encoding positive temperature
        encoded = characteristic.encode_value(21.48)
        assert encoded == bytearray([0x64, 0x08])

        # Test encoding zero
        encoded = characteristic.encode_value(0.0)
        assert encoded == bytearray([0x00, 0x00])

        # Test encoding negative temperature
        encoded = characteristic.encode_value(-10.0)
        assert encoded == bytearray([0x18, 0xFC])

    def test_characteristic_metadata(self, characteristic: TemperatureCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Temperature"
        assert characteristic.unit == "°C"
        assert characteristic.uuid == "2A6E"

    def test_temperature_precision(self, characteristic: TemperatureCharacteristic) -> None:
        """Test temperature precision (0.01°C resolution)."""
        # Test precision
        data = bytearray([0x01, 0x00])  # 1 = 0.01°C
        result = characteristic.decode_value(data)
        assert result == 0.01

        data = bytearray([0x0A, 0x00])  # 10 = 0.10°C
        result = characteristic.decode_value(data)
        assert result == 0.10
