"""Test cycling power feature characteristic parsing."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import CyclingPowerFeatureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


class TestCyclingPowerFeatureCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Feature characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerFeatureCharacteristic:
        """Provide Cycling Power Feature characteristic for testing."""
        return CyclingPowerFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Feature characteristic."""
        return "2A65"

    @pytest.fixture
    def valid_test_data(self) -> bytearray:
        """Valid cycling power feature test data."""
        return bytearray(struct.pack("<I", 0x0000001F))  # Multiple features enabled

    def test_cycling_power_feature_values(self, characteristic: CyclingPowerFeatureCharacteristic) -> None:
        """Test parsing cycling power feature values."""
        # Test basic feature mask
        feature_data = struct.pack("<I", 0x0000001F)  # Multiple features enabled
        result = characteristic.decode_value(bytearray(feature_data))
        assert result == 31

        # Test single feature
        feature_data = struct.pack("<I", 0x00000001)  # Only pedal power balance
        result = characteristic.decode_value(bytearray(feature_data))
        assert result == 1

        # Test no features
        feature_data = struct.pack("<I", 0x00000000)
        result = characteristic.decode_value(bytearray(feature_data))
        assert result == 0
