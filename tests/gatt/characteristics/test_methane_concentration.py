"""Test methane concentration characteristic parsing."""

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
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid methane concentration test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x64, 0x00]), expected_value=100, description="100 ppm methane concentration"
        )

    def test_methane_concentration_parsing(self, characteristic: MethaneConcentrationCharacteristic) -> None:
        """Test methane concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppm"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppm little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100
