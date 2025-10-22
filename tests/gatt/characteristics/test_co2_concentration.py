"""Test CO2 concentration characteristic parsing."""

import pytest

from bluetooth_sig.gatt.characteristics import CO2ConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests, CharacteristicTestData


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
    def valid_test_data(self) -> bytearray:
        """Valid CO2 concentration test data."""
        return bytearray([0x34, 0x12])  # 4660 ppm little endian

    def test_co2_concentration_boundary_values(self, characteristic: CO2ConcentrationCharacteristic) -> None:
        """Test CO2 concentration boundary values and validation."""
        # Test normal values
        test_data = bytearray([0x34, 0x12])  # 4660 ppm
        result = characteristic.decode_value(test_data)
        assert result == 4660

        # Test max valid value (65533 ppm)
        high_data = bytearray([0xFD, 0xFF])  # 65533 ppm
        result = characteristic.parse_value(high_data)
        assert result.parse_success
        assert result.value == 65533

    def test_co2_concentration_validation_limits(self, characteristic: CO2ConcentrationCharacteristic) -> None:
        """Test CO2 concentration validation rejects values above max."""
        # Test value above max_value (65534) - should fail validation
        invalid_data = bytearray([0xFE, 0xFF])  # 65534 ppm
        result = characteristic.parse_value(invalid_data)
        assert not result.parse_success
        assert "invalid value" in result.error_message.lower()
