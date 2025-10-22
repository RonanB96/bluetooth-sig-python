"""Test Non-Methane VOC concentration characteristic parsing."""

import math

import pytest

from bluetooth_sig.gatt.characteristics import NonMethaneVOCConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


class TestNonMethaneVOCConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Non-Methane VOC Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> NonMethaneVOCConcentrationCharacteristic:
        """Provide Non-Methane VOC Concentration characteristic for testing."""
        return NonMethaneVOCConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Non-Methane VOC Concentration characteristic."""
        return "2BD3"

    @pytest.fixture
    def valid_test_data(self) -> bytearray:
        """Valid Non-Methane VOC concentration test data."""
        return bytearray([0x34, 0x12])  # IEEE 11073 SFLOAT little endian

    def test_tvoc_concentration_parsing(self, characteristic: NonMethaneVOCConcentrationCharacteristic) -> None:
        """Test TVOC concentration characteristic parsing."""
        # Test metadata - Updated for SIG spec compliance (medfloat16, kg/m³)
        assert characteristic.unit == "kg/m³"
        assert characteristic.value_type_resolved.value == "float"  # IEEE 11073 SFLOAT format

        # Test normal parsing - IEEE 11073 SFLOAT format
        # Example: 0x1234 = exponent=1, mantissa=564 = 564 * 10^1 = 5640
        test_data = bytearray([0x34, 0x12])  # IEEE 11073 SFLOAT little endian
        parsed = characteristic.decode_value(test_data)
        assert isinstance(parsed, float)

    def test_tvoc_concentration_special_values(self, characteristic: NonMethaneVOCConcentrationCharacteristic) -> None:
        """Test TVOC concentration special values per IEEE 11073 SFLOAT."""
        # Test IEEE 11073 special values

        # Test 0x07FF (NaN)
        result = characteristic.decode_value(bytearray([0xFF, 0x07]))
        assert math.isnan(result), f"Expected NaN, got {result}"

        # Test 0x0800 (NRes - Not a valid result)
        result = characteristic.decode_value(bytearray([0x00, 0x08]))
        assert math.isnan(result), f"Expected NaN, got {result}"

        # Test 0x07FE (+INFINITY)
        result = characteristic.decode_value(bytearray([0xFE, 0x07]))
        assert math.isinf(result) and result > 0, f"Expected +inf, got {result}"

        # Test 0x0802 (-INFINITY)
        result = characteristic.decode_value(bytearray([0x02, 0x08]))
        assert math.isinf(result) and result < 0, f"Expected -inf, got {result}"
