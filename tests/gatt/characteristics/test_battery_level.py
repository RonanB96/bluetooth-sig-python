"""Tests for Battery Level characteristic (0x2A19)."""

import pytest

from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.constants import UINT8_MAX
from tests.gatt.characteristics.test_characteristic_common import (
    CommonCharacteristicTests,
)


class TestBatteryLevelCharacteristic(CommonCharacteristicTests):
    """Test Battery Level characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BatteryLevelCharacteristic:
        """Provide Battery Level characteristic for testing."""
        return BatteryLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Level characteristic."""
        return "2A19"

    def test_valid_battery_levels(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test parsing valid battery level values."""
        # Test minimum value
        data = bytearray([0])
        result = characteristic.decode_value(data)
        assert result == 0

        # Test typical value
        data = bytearray([50])
        result = characteristic.decode_value(data)
        assert result == 50

        # Test maximum value
        data = bytearray([100])
        result = characteristic.decode_value(data)
        assert result == 100

    def test_out_of_range_values(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test that out-of-range values raise appropriate errors."""
        # Test value above 100% should raise ValueError
        data = bytearray([150])
        with pytest.raises(ValueError, match="out of range"):
            characteristic.decode_value(data)

        # Test edge values
        data = bytearray([UINT8_MAX])
        with pytest.raises(ValueError, match="out of range"):
            characteristic.decode_value(data)

    def test_invalid_data_length(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test that invalid data lengths are handled properly."""
        # Test empty data should raise ValueError (not InsufficientDataError)
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray())

        # Test too much data (should work, extra ignored)
        data = bytearray([50, 60, 70])
        result = characteristic.decode_value(data)
        assert result == 50  # Only first byte used

    def test_encode_value(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test encoding battery level values."""
        # Test encoding valid values
        encoded = characteristic.encode_value(50)
        assert encoded == bytearray([50])

        encoded = characteristic.encode_value(100)
        assert encoded == bytearray([100])

        encoded = characteristic.encode_value(0)
        assert encoded == bytearray([0])

    def test_characteristic_metadata(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Battery Level"
        assert characteristic.unit == "%"
        assert characteristic.uuid == "2A19"
