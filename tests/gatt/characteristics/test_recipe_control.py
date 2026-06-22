from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.recipe_control import (  # type: ignore[import-untyped]
    RecipeControlCharacteristic,
    RecipeControlData,
    RecipeControlOpCode,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRecipeControlCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> RecipeControlCharacteristic:
        return RecipeControlCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C26"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), RecipeControlData(op_code=RecipeControlOpCode.READ), "read"),
            CharacteristicTestData(
                bytearray([0x01, 0x02, 0x00]),
                RecipeControlData(op_code=RecipeControlOpCode.START, cooking_step_index=2),
                "start step 2",
            ),
        ]

    def test_invalid_length_fails(self, characteristic: RecipeControlCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x01, 0x02]))

    def test_invalid_opcode_fails(self, characteristic: RecipeControlCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xFF]))
