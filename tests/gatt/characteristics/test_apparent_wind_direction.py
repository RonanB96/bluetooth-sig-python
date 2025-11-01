"""Test apparent wind direction characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.apparent_wind_direction import ApparentWindDirectionCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestApparentWindDirectionCharacteristic(CommonCharacteristicTests):
    """Test Apparent Wind Direction characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> ApparentWindDirectionCharacteristic:
        """Provide Apparent Wind Direction characteristic for testing."""
        return ApparentWindDirectionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Wind Direction characteristic."""
        return "2A73"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid apparent wind direction test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0.0,
                description="0° (bow/forward)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x28, 0x23]),
                expected_value=90.0,
                description="90° (starboard beam)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x27]),
                expected_value=100.0,
                description="100° wind direction",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x50, 0x46]),
                expected_value=180.0,
                description="180° (stern/aft)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x9F, 0x8C]),
                expected_value=359.99,
                description="359.99° (maximum)",
            ),
        ]

    def test_apparent_wind_direction_parsing(self, characteristic: ApparentWindDirectionCharacteristic) -> None:
        """Test apparent wind direction characteristic parsing."""
        direction_data = bytearray([0x10, 0x27])  # 10000 * 0.01 = 100.0°
        assert characteristic.decode_value(direction_data) == 100.0

    def test_apparent_wind_direction_cardinal_points(self, characteristic: ApparentWindDirectionCharacteristic) -> None:
        """Test apparent wind direction cardinal points."""
        # Bow (0°)
        data_bow = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data_bow) == 0.0

        # Starboard beam (90°)
        data_starboard = bytearray([0x28, 0x23])  # 9000 * 0.01 = 90.0
        assert characteristic.decode_value(data_starboard) == 90.0

        # Stern (180°)
        data_stern = bytearray([0x50, 0x46])  # 18000 * 0.01 = 180.0
        assert characteristic.decode_value(data_stern) == 180.0

        # Port beam (270°)
        data_port = bytearray([0x78, 0x69])  # 27000 * 0.01 = 270.0
        assert characteristic.decode_value(data_port) == 270.0

    def test_apparent_wind_direction_boundary_values(self, characteristic: ApparentWindDirectionCharacteristic) -> None:
        """Test boundary wind direction values."""
        # Minimum (0°)
        data_min = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data_min) == 0.0

        # Maximum (359.99°)
        data_max = bytearray([0x9F, 0x8C])  # 35999 * 0.01 = 359.99
        assert characteristic.decode_value(data_max) == 359.99
