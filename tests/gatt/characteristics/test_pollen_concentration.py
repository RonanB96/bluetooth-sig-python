"""Test pollen concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PollenConcentrationCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


class TestPollenConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Pollen Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PollenConcentrationCharacteristic:
        """Provide Pollen Concentration characteristic for testing."""
        return PollenConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Pollen Concentration characteristic."""
        return "2A75"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid pollen concentration test data."""
        return bytearray([0x40, 0xE2, 0x01]), 123456.0  # 123456 in 24-bit little endian

    def test_pollen_concentration_parsing(self, characteristic: PollenConcentrationCharacteristic) -> None:
        """Test Pollen Concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "grains/m³"

        # Test normal parsing: 123456 count/m³
        test_data = bytearray([0x40, 0xE2, 0x01])  # 123456 in 24-bit little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 123456.0  # Returns float now
