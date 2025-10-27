"""Test nitrogen dioxide concentration characteristic parsing."""

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
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid nitrogen dioxide concentration test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x32, 0x00]), expected_value=50, description="50 ppb nitrogen dioxide concentration"
        )

    def test_nitrogen_dioxide_concentration_parsing(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test nitrogen dioxide concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x32, 0x00])  # 50 ppb little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 50
