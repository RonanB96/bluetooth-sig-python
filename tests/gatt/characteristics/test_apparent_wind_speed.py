"""Test apparent wind speed characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.apparent_wind_speed import ApparentWindSpeedCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid apparent wind speed test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0.0 m/s (calm)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]), expected_value=1.0, description="1.0 m/s (light air)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xF4, 0x01]), expected_value=5.0, description="5.0 m/s (light breeze)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDC, 0x05]), expected_value=15.0, description="15.0 m/s (strong breeze)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=655.35, description="655.35 m/s (maximum)"
            ),
        ]

    def test_apparent_wind_speed_parsing(self, characteristic: ApparentWindSpeedCharacteristic) -> None:
        """Test apparent wind speed characteristic parsing."""
        # Test parsing similar to true wind
        speed_data = bytearray([0x64, 0x00])  # 100 * 0.01 = 1.0 m/s
        assert characteristic.decode_value(speed_data) == 1.0

    def test_apparent_wind_speed_boundary_values(self, characteristic: ApparentWindSpeedCharacteristic) -> None:
        """Test boundary apparent wind speed values."""
        # Calm
        data_min = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data_min) == 0.0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.decode_value(data_max) == 655.35

    def test_apparent_wind_speed_various_conditions(self, characteristic: ApparentWindSpeedCharacteristic) -> None:
        """Test apparent wind speed under various conditions."""
        # Light breeze (5 m/s)
        data_light = bytearray([0xF4, 0x01])  # 500 * 0.01
        assert characteristic.decode_value(data_light) == 5.0

        # Strong breeze (15 m/s)
        data_strong = bytearray([0xDC, 0x05])  # 1500 * 0.01
        assert characteristic.decode_value(data_strong) == 15.0
