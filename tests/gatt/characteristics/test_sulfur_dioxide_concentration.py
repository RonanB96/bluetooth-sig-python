"""Test sulfur dioxide concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SulfurDioxideConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSulfurDioxideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Sulfur Dioxide Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> SulfurDioxideConcentrationCharacteristic:
        """Provide Sulfur Dioxide Concentration characteristic for testing."""
        return SulfurDioxideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Sulfur Dioxide Concentration characteristic."""
        return "2BD8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid sulfur dioxide concentration test data.

        GSS: medfloat16 (IEEE 11073 SFLOAT), unit kg/m³.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x14, 0x80]),  # SFLOAT mantissa=20, exp=0 → 20.0
                expected_value=20.0,
                description="20.0 kg/m³",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x80]),  # SFLOAT mantissa=100, exp=0 → 100.0
                expected_value=100.0,
                description="100.0 kg/m³",
            ),
        ]

    def test_sulfur_dioxide_concentration_parsing(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test sulfur dioxide concentration characteristic parsing."""
        assert characteristic.unit == "kg/m³"
        assert characteristic.parse_value(bytearray([0x64, 0x80])) == 100.0

    def test_sulfur_dioxide_concentration_boundary_values(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test boundary values for SO2 concentration."""
        assert characteristic.parse_value(bytearray([0x00, 0x80])) == 0.0

    def test_sulfur_dioxide_concentration_typical_levels(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test typical SO2 concentration levels."""
        assert characteristic.parse_value(bytearray([0x14, 0x80])) == 20.0
