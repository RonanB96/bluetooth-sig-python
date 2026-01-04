"""Test elevation characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ElevationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestElevationCharacteristic(CommonCharacteristicTests):
    """Test Elevation characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> ElevationCharacteristic:
        """Provide Elevation characteristic for testing."""
        return ElevationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Elevation characteristic."""
        return "2A6C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid elevation test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x50, 0xC3, 0x00]), expected_value=500.0, description="500.0 m (typical city)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xA0, 0x86, 0x01]), expected_value=1000.0, description="1000.0 m (mountain town)"
            ),
        ]

    def test_elevation_parsing(self, characteristic: ElevationCharacteristic) -> None:
        """Test Elevation characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.value_type.value == "float"

        # Test normal parsing: 50000 (in 0.01 meters) = 500.00 meters
        test_data = bytearray([0x50, 0xC3, 0x00])  # 50000 in 24-bit little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed.value == 500.0

        # Test negative elevation (below sea level)
        neg_data = bytearray([0xFF, 0xFF, 0xFF])  # -1 in 24-bit signed
        parsed_neg = characteristic.parse_value(neg_data)
        assert parsed_neg.value == -0.01

    def test_elevation_error_handling(self, characteristic: ElevationCharacteristic) -> None:
        """Test Elevation error handling."""
        # Test insufficient data - parse_value returns parse_success=False
        result = characteristic.parse_value(bytearray([0x12, 0x34]))
        assert result.parse_success is False
        assert "3 bytes" in (result.error_message or "")

    def test_elevation_boundary_values(self, characteristic: ElevationCharacteristic) -> None:
        """Test elevation boundary values."""
        # Sea level
        data_sea = bytearray([0x00, 0x00, 0x00])
        assert characteristic.parse_value(data_sea).value == 0.0

        # Below sea level (Dead Sea: -550m)
        data_below = bytearray([0x28, 0x29, 0xFF])  # -55000 * 0.01 = -550.0
        result = characteristic.parse_value(data_below)
        assert abs(result.value - (-550.0)) < 0.1  # Allow small floating point error

    def test_elevation_famous_heights(self, characteristic: ElevationCharacteristic) -> None:
        """Test elevations of famous locations."""
        # Mt. Everest (8848m)
        data_everest = bytearray([0x40, 0x80, 0x0D])  # 884800 * 0.01 = 8848.0
        result = characteristic.parse_value(data_everest)
        assert abs(result.value - 8848.0) < 0.1

        # Denver "Mile High City" (~1600m)
        data_denver = bytearray([0x00, 0x71, 0x02])  # 160000 * 0.01 = 1600.0
        result = characteristic.parse_value(data_denver)
        assert abs(result.value - 1600.0) < 0.1
