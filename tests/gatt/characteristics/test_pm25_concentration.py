"""Test PM2.5 concentration characteristic parsing."""

import pytest

from bluetooth_sig.gatt.characteristics import PM25ConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


class TestPM25ConcentrationCharacteristic(CommonCharacteristicTests):
    """Test PM2.5 Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PM25ConcentrationCharacteristic:
        """Provide PM2.5 Concentration characteristic for testing."""
        return PM25ConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PM2.5 Concentration characteristic."""
        return "2BD6"

    @pytest.fixture
    def valid_test_data(self) -> bytearray:
        """Valid PM2.5 concentration test data."""
        return bytearray([0x19, 0x00])  # 25 µg/m³ little endian

    def test_pm25_concentration_parsing(self, characteristic: PM25ConcentrationCharacteristic) -> None:
        """Test PM2.5 concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "µg/m³"

        # Test normal parsing
        test_data = bytearray([0x19, 0x00])  # 25 µg/m³ little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 25
