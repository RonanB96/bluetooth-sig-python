"""Test apparent wind speed characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.apparent_wind_speed import ApparentWindSpeedCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


class TestApparentWindSpeedCharacteristic(CommonCharacteristicTests):
    """Test Apparent Wind Speed characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> ApparentWindSpeedCharacteristic:
        """Provide Apparent Wind Speed characteristic for testing."""
        return ApparentWindSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Wind Speed characteristic."""
        return "2A72"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid apparent wind speed test data."""
        return bytearray([0x64, 0x00]), 1.0  # 100 * 0.01 = 1.0 m/s

    def test_apparent_wind_speed_parsing(self, characteristic: ApparentWindSpeedCharacteristic) -> None:
        """Test apparent wind speed characteristic parsing."""
        # Test parsing similar to true wind
        speed_data = bytearray([0x64, 0x00])  # 100 * 0.01 = 1.0 m/s
        assert characteristic.decode_value(speed_data) == 1.0
