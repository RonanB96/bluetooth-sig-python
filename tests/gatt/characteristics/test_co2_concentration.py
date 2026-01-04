"""Test CO2 concentration characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CO2ConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCO2ConcentrationCharacteristic(CommonCharacteristicTests):
    """Test CO2 Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CO2ConcentrationCharacteristic:
        """Provide CO2 Concentration characteristic for testing."""
        return CO2ConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CO2 Concentration characteristic."""
        return "2B8C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid CO2 concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x34, 0x12]), expected_value=4660, description="4660 ppm CO2 concentration"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x90, 0x01]), expected_value=400, description="400 ppm typical outdoor CO2"
            ),
        ]

    def test_co2_concentration_boundary_values(self, characteristic: CO2ConcentrationCharacteristic) -> None:
        """Test CO2 concentration boundary values and validation."""
        # Test normal values
        test_data = bytearray([0x34, 0x12])  # 4660 ppm
        result = characteristic.parse_value(test_data)
        assert result.value == 4660

        # Test max valid value (65533 ppm)
        high_data = bytearray([0xFD, 0xFF])  # 65533 ppm
        result = characteristic.parse_value(high_data)
        assert result.parse_success
        assert result.value == 65533

    def test_co2_concentration_validation_limits(self, characteristic: CO2ConcentrationCharacteristic) -> None:
        """Test CO2 concentration special value handling at overflow boundary."""
        # Test 0xFFFE (65534) - special value meaning "65534 or greater" per SIG spec
        overflow_data = bytearray([0xFE, 0xFF])  # 65534 / 0xFFFE
        result = characteristic.parse_value(overflow_data)
        assert result.parse_success
        assert result.special_value is not None
        assert result.special_value.raw_value == 65534
        assert "65534 or greater" in result.value.meaning.lower()

        # Test 0xFFFF (65535) - special value meaning "not known"
        unknown_data = bytearray([0xFF, 0xFF])  # 65535 / 0xFFFF
        result = characteristic.parse_value(unknown_data)
        assert result.parse_success
        assert result.special_value is not None
        assert result.special_value.raw_value == 65535
        assert "not known" in result.value.meaning.lower()
