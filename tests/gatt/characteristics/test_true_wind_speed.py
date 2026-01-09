"""Test true wind speed characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.true_wind_speed import TrueWindSpeedCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrueWindSpeedCharacteristic(CommonCharacteristicTests):
    """Test True Wind Speed characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> TrueWindSpeedCharacteristic:
        """Provide True Wind Speed characteristic for testing."""
        return TrueWindSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for True Wind Speed characteristic."""
        return "2A70"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid true wind speed test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0.0 m/s (calm)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xF4, 0x01]), expected_value=5.0, description="5.0 m/s (light breeze)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x1A, 0x04]), expected_value=10.50, description="10.50 m/s (fresh breeze)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDC, 0x05]), expected_value=15.0, description="15.0 m/s (strong breeze)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=655.35, description="655.35 m/s (maximum)"
            ),
        ]

    def test_true_wind_speed_parsing(self, characteristic: TrueWindSpeedCharacteristic) -> None:
        """Test true wind speed characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m/s"

        # Test 10.50 m/s (1050 * 0.01)
        data = bytearray([0x1A, 0x04])  # 1050 in little endian
        assert characteristic.parse_value(data) == 10.50

        # Test zero wind
        data = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data) == 0.0

    def test_true_wind_speed_boundary_values(self, characteristic: TrueWindSpeedCharacteristic) -> None:
        """Test boundary wind speed values."""
        # Minimum (calm)
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min) == 0.0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max) == 655.35

    def test_true_wind_speed_beaufort_scale_examples(self, characteristic: TrueWindSpeedCharacteristic) -> None:
        """Test wind speeds corresponding to Beaufort scale."""
        # Light breeze (5 m/s, Beaufort 3)
        data_light = bytearray([0xF4, 0x01])  # 500 * 0.01 = 5.0
        assert characteristic.parse_value(data_light) == 5.0

        # Fresh breeze (10.5 m/s, Beaufort 5)
        data_fresh = bytearray([0x1A, 0x04])  # 1050 * 0.01 = 10.50
        assert characteristic.parse_value(data_fresh) == 10.50

        # Strong breeze (15 m/s, Beaufort 6)
        data_strong = bytearray([0xDC, 0x05])  # 1500 * 0.01 = 15.0
        assert characteristic.parse_value(data_strong) == 15.0
