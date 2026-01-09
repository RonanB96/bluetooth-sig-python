"""Test rainfall characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import RainfallCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRainfallCharacteristic(CommonCharacteristicTests):
    """Test Rainfall characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> RainfallCharacteristic:
        """Provide Rainfall characteristic for testing."""
        return RainfallCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Rainfall characteristic."""
        return "2A78"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid rainfall test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0.0 mm (no rain)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00]), expected_value=10.0, description="10.0 mm (light rain)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]), expected_value=100.0, description="100.0 mm (moderate rain)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE2, 0x04]), expected_value=1250.0, description="1250.0 mm (heavy rain)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=65535.0, description="65535.0 mm (maximum)"
            ),
        ]

    def test_rainfall_parsing(self, characteristic: RainfallCharacteristic) -> None:
        """Test Rainfall characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "mm"

        # Test normal parsing: 1250 mm rainfall
        test_data = bytearray([0xE2, 0x04])  # 1250 in little endian uint16
        parsed = characteristic.parse_value(test_data)
        assert parsed == 1250.0

    def test_rainfall_boundary_values(self, characteristic: RainfallCharacteristic) -> None:
        """Test rainfall boundary values."""
        # No rainfall
        data_zero = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_zero) == 0.0

        # Maximum rainfall
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max) == 65535.0

    def test_rainfall_typical_values(self, characteristic: RainfallCharacteristic) -> None:
        """Test typical rainfall values."""
        # Light rain (10 mm)
        data_light = bytearray([0x0A, 0x00])
        assert characteristic.parse_value(data_light) == 10.0

        # Moderate rain (100 mm)
        data_moderate = bytearray([0x64, 0x00])
        assert characteristic.parse_value(data_moderate) == 100.0
