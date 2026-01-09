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
        """Valid methane concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00]), expected_value=2, description="2 ppm (typical atmosphere)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00]), expected_value=50, description="50 ppm (elevated)"
            ),
        ]

    def test_methane_concentration_parsing(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test methane concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppm"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppm little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed == 100

    def test_methane_concentration_boundary_values(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test boundary methane concentration values."""
        # No methane
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min) == 0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max) == 65535

    def test_methane_concentration_typical_levels(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test typical methane concentration levels."""
        # Atmospheric level (2 ppm)
        data_atm = bytearray([0x02, 0x00])
        assert characteristic.parse_value(data_atm) == 2

        # Elevated (50 ppm)
        data_elevated = bytearray([0x32, 0x00])
        assert characteristic.parse_value(data_elevated) == 50
