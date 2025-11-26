from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ManufacturerNameStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestManufacturerNameStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = ManufacturerNameStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return ManufacturerNameStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A29"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Apple Inc."), expected_value="Apple Inc.", description="Apple manufacturer name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Samsung Electronics"),
                expected_value="Samsung Electronics",
                description="Samsung manufacturer name",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Google LLC"),
                expected_value="Google LLC",
                description="Google manufacturer name",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty manufacturer name"),
        ]

    def test_invalid_utf8_raises_value_error(self, characteristic: BaseCharacteristic) -> None:
        """Test that invalid UTF-8 data raises ValueError."""
        invalid_utf8 = bytearray([0xFF, 0xFE, 0xFD])  # Invalid UTF-8 sequence
        with pytest.raises(ValueError, match="Invalid UTF-8 string data"):
            characteristic.decode_value(invalid_utf8)

    def test_null_terminated_string_handling(self, characteristic: BaseCharacteristic) -> None:
        """Test that null-terminated strings are handled correctly."""
        data_with_null = bytearray(b"Test\x00Extra")
        result = characteristic.decode_value(data_with_null)
        assert result == "Test"  # Should stop at null terminator
