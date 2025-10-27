"""Test true wind direction characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.true_wind_direction import TrueWindDirectionCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrueWindDirectionCharacteristic(CommonCharacteristicTests):
    """Test True Wind Direction characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> TrueWindDirectionCharacteristic:
        """Provide True Wind Direction characteristic for testing."""
        return TrueWindDirectionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for True Wind Direction characteristic."""
        return "2A71"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid true wind direction test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x50, 0x46]), expected_value=180.0, description="180° true wind direction"
        )

    def test_true_wind_direction_parsing(self, characteristic: TrueWindDirectionCharacteristic) -> None:
        """Test true wind direction characteristic parsing."""
        # Test 180.0° (18000 * 0.01)
        data = bytearray([0x50, 0x46])  # 18000 in little endian
        assert characteristic.decode_value(data) == 180.0

        # Test 0° (north)
        data = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data) == 0.0
