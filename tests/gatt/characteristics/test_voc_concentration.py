"""Test VOC concentration characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import VOCConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVOCConcentrationCharacteristic(CommonCharacteristicTests):
    """Test VOC Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> VOCConcentrationCharacteristic:
        """Provide VOC Concentration characteristic for testing."""
        return VOCConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for VOC Concentration characteristic."""
        return "2BE7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid VOC concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x04]), expected_value=1024, description="1024 ppb VOC concentration"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x00]), expected_value=200, description="200 ppb VOC concentration"
            ),
        ]

    def test_voc_concentration_parsing(self, characteristic: VOCConcentrationCharacteristic) -> None:
        """Test VOC concentration characteristic parsing."""
        # Test metadata - Updated for SIG spec compliance (uint16, ppb)
        assert characteristic.unit == "ppb"
        assert characteristic.value_type_resolved.value == "int"  # uint16 format

        # Test normal value parsing
        test_data = bytearray([0x00, 0x04])  # 1024 ppb
        result = characteristic.parse_value(test_data)
        assert result == 1024

        # Test encoding
        encoded = characteristic.build_value(1024)
        assert encoded == bytearray([0x00, 0x04])

    def test_voc_concentration_special_values(self, characteristic: VOCConcentrationCharacteristic) -> None:
        """Test VOC concentration special values per SIG specification."""
        # Test 0xFFFE (value is 65534 or greater per SIG spec)
        test_data = bytearray([0xFE, 0xFF])
        result = characteristic.parse_value(test_data)

        assert result is not None
        assert hasattr(result, "raw_value")
        assert result.raw_value == 65534

        # Test 0xFFFF (value is not known per SIG spec)
        # The uint16 template returns the raw value 65535
        test_data = bytearray([0xFF, 0xFF])
        result = characteristic.parse_value(test_data)

        assert result is not None
        assert hasattr(result, "raw_value")
        assert result.raw_value == 65535

        # Test encoding of normal values
        encoded = characteristic.build_value(1024)
        assert encoded == bytearray([0x00, 0x04])

        # Test encoding of maximum normal value
        encoded = characteristic.build_value(65533)
        assert encoded == bytearray([0xFD, 0xFF])

        # NOTE: Cannot encode special values 65534/65535 as they fail validation
        # This is expected behavior - special values are for reading only
