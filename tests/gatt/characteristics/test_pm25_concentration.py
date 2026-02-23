"""Test PM2.5 concentration characteristic parsing."""

from __future__ import annotations

import math

import pytest

from bluetooth_sig.gatt.characteristics import PM25ConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid PM2.5 concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x19, 0x80]),  # 25 in IEEE 11073 SFLOAT
                expected_value=25.0,
                description="25.0 kg/m\u00b3 PM2.5 concentration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x80]),  # 50 in IEEE 11073 SFLOAT
                expected_value=50.0,
                description="50.0 kg/m\u00b3 PM2.5 concentration",
            ),
        ]

    def test_pm25_concentration_parsing(self, characteristic: PM25ConcentrationCharacteristic) -> None:
        """Test PM2.5 concentration characteristic parsing."""
        assert characteristic.unit == "kg/m\u00b3"
        assert characteristic.python_type is float

        test_data = bytearray([0x19, 0x80])  # mantissa=25, exponent=0 → 25.0
        parsed = characteristic.parse_value(test_data)
        assert isinstance(parsed, float)
        assert parsed == 25.0

    def test_pm25_concentration_special_values(self, characteristic: PM25ConcentrationCharacteristic) -> None:
        """Test PM2.5 concentration special values per IEEE 11073 SFLOAT."""
        # Test NaN special value (0x07FF)
        result = characteristic.parse_value(bytearray([0xFF, 0x07]))
        assert math.isnan(result)

        # Test NRes special value (0x0800)
        result = characteristic.parse_value(bytearray([0x00, 0x08]))
        assert math.isnan(result)

        # Test positive infinity (0x07FE)
        result = characteristic.parse_value(bytearray([0xFE, 0x07]))
        assert math.isinf(result) and result > 0

        # Test negative infinity (0x0802)
        result = characteristic.parse_value(bytearray([0x02, 0x08]))
        assert math.isinf(result) and result < 0
