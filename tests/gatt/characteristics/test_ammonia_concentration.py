"""Test ammonia concentration characteristic parsing."""

from __future__ import annotations

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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid ammonia concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x80]),  # 10 in IEEE 11073 SFLOAT
                expected_value=10.0,
                description="10 ppm ammonia concentration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x80]),  # 100 in IEEE 11073 SFLOAT
                expected_value=100.0,
                description="100 ppm ammonia concentration",
            ),
        ]

    def test_ammonia_concentration_parsing(self, characteristic: AmmoniaConcentrationCharacteristic) -> None:
        """Test ammonia concentration characteristic parsing."""
        # Test metadata - Updated for SIG spec compliance (medfloat16, kg/m³)
        assert characteristic.unit == "kg/m³"
        assert characteristic.python_type is float  # YAML specifies medfloat16 format
