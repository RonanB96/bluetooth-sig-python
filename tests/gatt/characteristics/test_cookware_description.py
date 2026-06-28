from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cookware_description import (  # type: ignore[import-untyped]
    CookwareDescriptionCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookwareDescriptionCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookwareDescriptionCharacteristic:
        return CookwareDescriptionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C25"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Pan Model X"), "Pan Model X", "ascii name"),
            CharacteristicTestData(bytearray("Cafetière".encode()), "Cafetière", "utf-8 name"),
        ]

    def test_parse_invalid_utf8_fails(self, characteristic: CookwareDescriptionCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xFF, 0xFE, 0xFD]))

    def test_build_too_long_string_fails(self, characteristic: CookwareDescriptionCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value("x" * 300)
