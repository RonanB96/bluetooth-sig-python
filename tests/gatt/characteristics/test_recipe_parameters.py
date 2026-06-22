from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.recipe_parameters import (  # type: ignore[import-untyped]
    RecipeParametersCharacteristic,
    RecipeParametersData,
    RecipeParametersFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRecipeParametersCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> RecipeParametersCharacteristic:
        return RecipeParametersCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C27"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x00, 0x00, 0x01, 0x00, 0x00]),
                RecipeParametersData(flags=RecipeParametersFlags(0), cooking_step_index=1, cooking_process_type=0),
                "minimal no-cooking",
            ),
            CharacteristicTestData(
                bytearray([0x48, 0x00, 0x03, 0x00, 0x01, 0x2C, 0x01, 0x96, 0x00, 0x0F, 0x00]),
                RecipeParametersData(
                    flags=RecipeParametersFlags.TEMPERATURE_PRESENT
                    | RecipeParametersFlags.TERMINATION_CONDITION_PRESENT,
                    cooking_step_index=3,
                    cooking_process_type=1,
                    duration_seconds=300,
                    temperature=15.0,
                    termination_condition=15,
                ),
                "duration + temperature + termination",
            ),
        ]

    def test_short_payload_fails(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x00, 0x01]))

    def test_missing_temperature_field_for_build_fails(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(
                RecipeParametersData(
                    flags=RecipeParametersFlags.TEMPERATURE_PRESENT,
                    cooking_step_index=1,
                    cooking_process_type=0,
                )
            )
