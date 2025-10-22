"""Test ozone concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import OzoneConcentrationCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


class TestOzoneConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Ozone Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> OzoneConcentrationCharacteristic:
        """Provide Ozone Concentration characteristic for testing."""
        return OzoneConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Ozone Concentration characteristic."""
        return "2BD4"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid ozone concentration test data."""
        return bytearray([0x64, 0x00]), 100.0  # 100 ppb little endian

    def test_ozone_concentration_parsing(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppb little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100
