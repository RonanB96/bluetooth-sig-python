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
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid elevation test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x50, 0xC3, 0x00]), expected_value=500.0, description="500.0 meters elevation"
        )

    def test_elevation_parsing(self, characteristic: ElevationCharacteristic) -> None:
        """Test Elevation characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.value_type.value == "float"

        # Test normal parsing: 50000 (in 0.01 meters) = 500.00 meters
        test_data = bytearray([0x50, 0xC3, 0x00])  # 50000 in 24-bit little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 500.0

        # Test negative elevation (below sea level)
        neg_data = bytearray([0xFF, 0xFF, 0xFF])  # -1 in 24-bit signed
        parsed_neg = characteristic.decode_value(neg_data)
        assert parsed_neg == -0.01

    def test_elevation_error_handling(self, characteristic: ElevationCharacteristic) -> None:
        """Test Elevation error handling."""
        # Test insufficient data
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x12, 0x34]))
