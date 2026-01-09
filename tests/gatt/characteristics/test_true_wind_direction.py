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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid true wind direction test data."""
        return [
            CharacteristicTestData(input_data=bytearray([0x28, 0x23]), expected_value=90.0, description="90° (East)"),
            CharacteristicTestData(
                input_data=bytearray([0x50, 0x46]), expected_value=180.0, description="180° (South)"
            ),
        ]

    def test_true_wind_direction_parsing(self, characteristic: TrueWindDirectionCharacteristic) -> None:
        """Test true wind direction characteristic parsing."""
        # Test 180.0° (18000 * 0.01)
        data = bytearray([0x50, 0x46])  # 18000 in little endian
        assert characteristic.parse_value(data) == 180.0

        # Test 0° (north)
        data = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data) == 0.0

    def test_true_wind_direction_cardinal_directions(self, characteristic: TrueWindDirectionCharacteristic) -> None:
        """Test cardinal wind directions."""
        # North (0°)
        data_north = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_north) == 0.0

        # East (90°)
        data_east = bytearray([0x28, 0x23])  # 9000 * 0.01 = 90.0
        assert characteristic.parse_value(data_east) == 90.0

        # South (180°)
        data_south = bytearray([0x50, 0x46])  # 18000 * 0.01 = 180.0
        assert characteristic.parse_value(data_south) == 180.0

        # West (270°)
        data_west = bytearray([0x78, 0x69])  # 27000 * 0.01 = 270.0
        assert characteristic.parse_value(data_west) == 270.0

    def test_true_wind_direction_boundary_values(self, characteristic: TrueWindDirectionCharacteristic) -> None:
        """Test boundary values for wind direction."""
        # Minimum (0°)
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min) == 0.0

        # Maximum (359.99°)
        data_max = bytearray([0x9F, 0x8C])  # 35999 * 0.01 = 359.99
        assert characteristic.parse_value(data_max) == 359.99
