"""Test ammonia concentration characteristic parsing."""

import pytest

from bluetooth_sig.gatt.characteristics import AmmoniaConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAmmoniaConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Ammonia Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> AmmoniaConcentrationCharacteristic:
        """Provide Ammonia Concentration characteristic for testing."""
        return AmmoniaConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Ammonia Concentration characteristic."""
        return "2BCF"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid ammonia concentration test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x34, 0x12]),  # IEEE 11073 SFLOAT little endian
            expected_value=5640.0,  # Expected parsed concentration value
            description="Valid ammonia concentration",
        )

    def test_ammonia_concentration_parsing(self, characteristic: AmmoniaConcentrationCharacteristic) -> None:
        """Test ammonia concentration characteristic parsing."""
        # Test metadata - Updated for SIG spec compliance (medfloat16, kg/m³)
        assert characteristic.unit == "kg/m³"
        assert characteristic.value_type_resolved.value == "float"  # YAML specifies medfloat16 format
