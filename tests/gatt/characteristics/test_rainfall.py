"""Test rainfall characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import RainfallCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid rainfall test data."""
        return bytearray([0xE2, 0x04]), 1250.0  # 1250 in little endian uint16

    def test_rainfall_parsing(self, characteristic: RainfallCharacteristic) -> None:
        """Test Rainfall characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "mm"

        # Test normal parsing: 1250 mm rainfall
        test_data = bytearray([0xE2, 0x04])  # 1250 in little endian uint16
        parsed = characteristic.decode_value(test_data)
        assert parsed == 1250.0
