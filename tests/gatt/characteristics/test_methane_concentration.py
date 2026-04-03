"""Test methane concentration characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MethaneConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMethaneConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Methane Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> MethaneConcentrationCharacteristic:
        """Provide Methane Concentration characteristic for testing."""
        return MethaneConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Methane Concentration characteristic."""
        return "2BD1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid methane concentration test data.

        GSS: medfloat16 (IEEE 11073 SFLOAT), unit ppb.
        SFLOAT byte pattern: [mantissa_lo, (exp_nibble<<4)|mantissa_hi].
        Exponent bias=8, so exp=0 → raw nibble=8 → high byte 0x80.
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x80]),  # SFLOAT mantissa=2, exp=0 → 2.0 ppb
                expected_value=2.0,
                description="2 ppb (typical atmosphere)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x80]),  # SFLOAT mantissa=50, exp=0 → 50.0 ppb
                expected_value=50.0,
                description="50 ppb (elevated)",
            ),
        ]

    def test_methane_concentration_parsing(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test methane concentration characteristic parsing."""
        assert characteristic.unit == "ppb"
        assert characteristic.parse_value(bytearray([0x64, 0x80])) == 100.0  # 100 ppb

    def test_methane_concentration_boundary_values(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test boundary methane concentration values."""
        assert characteristic.parse_value(bytearray([0x00, 0x80])) == 0.0

    def test_methane_concentration_typical_levels(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test typical methane concentration levels."""
        assert characteristic.parse_value(bytearray([0x02, 0x80])) == 2.0
        assert characteristic.parse_value(bytearray([0x32, 0x80])) == 50.0
