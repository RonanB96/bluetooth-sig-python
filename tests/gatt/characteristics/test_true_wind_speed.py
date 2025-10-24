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
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid true wind speed test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x1A, 0x04]), expected_value=10.50, description="10.50 m/s true wind speed"
        )

    def test_true_wind_speed_parsing(self, characteristic: TrueWindSpeedCharacteristic) -> None:
        """Test true wind speed characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "metres per second"

        # Test 10.50 m/s (1050 * 0.01)
        data = bytearray([0x1A, 0x04])  # 1050 in little endian
        assert characteristic.decode_value(data) == 10.50

        # Test zero wind
        data = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data) == 0.0
