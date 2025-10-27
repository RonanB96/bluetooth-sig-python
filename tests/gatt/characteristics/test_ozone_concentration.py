"""Test ozone concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import OzoneConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


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
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid ozone concentration test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x64, 0x00]), expected_value=100.0, description="100.0 ppb ozone concentration"
        )

    def test_ozone_concentration_parsing(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppb little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100
