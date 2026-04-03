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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid ozone concentration test data.

        GSS: medfloat16 (IEEE 11073 SFLOAT), unit kg/m³.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x80]),  # SFLOAT mantissa=50, exp=0 → 50.0
                expected_value=50.0,
                description="50.0 kg/m³",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x80]),  # SFLOAT mantissa=100, exp=0 → 100.0
                expected_value=100.0,
                description="100.0 kg/m³",
            ),
        ]

    def test_ozone_concentration_parsing(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration characteristic parsing."""
        assert characteristic.unit == "kg/m³"
        assert characteristic.parse_value(bytearray([0x64, 0x80])) == 100.0

    def test_ozone_concentration_boundary_values(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration boundary values."""
        assert characteristic.parse_value(bytearray([0x00, 0x80])) == 0.0

    def test_ozone_concentration_typical_values(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test typical ozone concentration values."""
        assert characteristic.parse_value(bytearray([0x32, 0x80])) == 50.0
        assert characteristic.parse_value(bytearray([0x64, 0x80])) == 100.0
