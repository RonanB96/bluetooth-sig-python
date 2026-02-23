"""Test PM1 concentration characteristic parsing."""

from __future__ import annotations

import math

import pytest

from bluetooth_sig.gatt.characteristics import PM1ConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPM1ConcentrationCharacteristic(CommonCharacteristicTests):
    """Test PM1 Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PM1ConcentrationCharacteristic:
        """Provide PM1 Concentration characteristic for testing."""
        return PM1ConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PM1 Concentration characteristic."""
        return "2BD5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid PM1 concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x80]),  # 10 in IEEE 11073 SFLOAT
                expected_value=10.0,
                description="10.0 kg/m\u00b3 PM1 concentration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x80]),  # 50 in IEEE 11073 SFLOAT
                expected_value=50.0,
                description="50.0 kg/m\u00b3 PM1 concentration",
            ),
        ]

    def test_pm1_concentration_parsing(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration characteristic parsing."""
        assert characteristic.unit == "kg/m\u00b3"
        assert characteristic.python_type is float

        # IEEE 11073 SFLOAT: exponent in top 4 bits, mantissa in lower 12
        test_data = bytearray([0x64, 0x80])  # mantissa=100, exponent=0 → 100.0
        parsed = characteristic.parse_value(test_data)
        assert isinstance(parsed, float)
        assert parsed == 100.0

    def test_pm1_concentration_special_values(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration special values per IEEE 11073 SFLOAT."""
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
