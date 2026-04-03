"""Test nitrogen dioxide concentration characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import NitrogenDioxideConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNitrogenDioxideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Nitrogen Dioxide Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> NitrogenDioxideConcentrationCharacteristic:
        """Provide Nitrogen Dioxide Concentration characteristic for testing."""
        return NitrogenDioxideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Nitrogen Dioxide Concentration characteristic."""
        return "2BD2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid nitrogen dioxide concentration test data.

        GSS: medfloat16 (IEEE 11073 SFLOAT), unit kg/m³.
        SFLOAT: [mantissa_lo, (exp_nibble<<4)|mantissa_hi], bias=8.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x28, 0x80]),  # SFLOAT mantissa=40, exp=0 → 40.0
                expected_value=40.0,
                description="40.0 kg/m³",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x80]),  # SFLOAT mantissa=200, exp=0 → 200.0
                expected_value=200.0,
                description="200.0 kg/m³",
            ),
        ]

    def test_nitrogen_dioxide_concentration_parsing(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test nitrogen dioxide concentration characteristic parsing."""
        assert characteristic.unit == "kg/m³"
        assert characteristic.parse_value(bytearray([0x32, 0x80])) == 50.0

    def test_nitrogen_dioxide_concentration_boundary_values(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test boundary NO2 concentration values."""
        assert characteristic.parse_value(bytearray([0x00, 0x80])) == 0.0

    def test_nitrogen_dioxide_concentration_typical_levels(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test typical NO2 concentration levels."""
        assert characteristic.parse_value(bytearray([0x28, 0x80])) == 40.0
        assert characteristic.parse_value(bytearray([0xC8, 0x80])) == 200.0
