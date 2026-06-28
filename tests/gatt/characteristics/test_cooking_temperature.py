from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_temperature import (  # type: ignore[import-untyped]
    CookingTemperatureCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingTemperatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingTemperatureCharacteristic:
        return CookingTemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x7B, 0x00]), 12.3, "12.3 C"),
            CharacteristicTestData(bytearray([0x9C, 0xFF]), -10.0, "-10 C"),
        ]

    def test_short_payload_fails(self, characteristic: CookingTemperatureCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x10]))

    def test_out_of_range_build_fails(self, characteristic: CookingTemperatureCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(5000.0)

    def test_unknown_sentinel_raises_special_value(self, characteristic: CookingTemperatureCharacteristic) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x80]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN
