from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.recipe_parameters import (  # type: ignore[import-untyped]
    CookingProcessType,
    RecipeParametersCharacteristic,
    RecipeParametersData,
    RecipeParametersFlags,
    TerminationConditionFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

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
                RecipeParametersData(
                    flags=RecipeParametersFlags(0),
                    cooking_step_index=1,
                    cooking_process_type=CookingProcessType.NO_COOKING,
                ),
                "minimal no-cooking",
            ),
            CharacteristicTestData(
                bytearray([0x48, 0x00, 0x03, 0x00, 0x01, 0x2C, 0x01, 0x96, 0x00, 0x05, 0x80]),
                RecipeParametersData(
                    flags=RecipeParametersFlags.TEMPERATURE_PRESENT
                    | RecipeParametersFlags.TERMINATION_CONDITION_PRESENT,
                    cooking_step_index=3,
                    cooking_process_type=CookingProcessType.PREHEATING,
                    duration_seconds=300,
                    temperature=15.0,
                    termination_condition=(
                        TerminationConditionFlags.TEMPERATURE_INCREASE
                        | TerminationConditionFlags.HUMIDITY_INCREASE
                        | TerminationConditionFlags.LOGICAL_AND
                    ),
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
                    cooking_process_type=CookingProcessType.NO_COOKING,
                )
            )

    def test_gradient_not_encoded_without_temperature_flag(
        self, characteristic: RecipeParametersCharacteristic
    ) -> None:
        """Encode must not emit gradient without TEMPERATURE_PRESENT (spec symmetry)."""
        data = RecipeParametersData(
            flags=RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT,
            cooking_step_index=1,
            cooking_process_type=CookingProcessType.NO_COOKING,
            temperature_gradient=1.0,
        )
        encoded = characteristic.build_value(data)
        assert len(encoded) == 5

    def test_temperature_and_gradient_round_trip(self, characteristic: RecipeParametersCharacteristic) -> None:
        """Temperature gradient encodes only when temperature is also present."""
        data = RecipeParametersData(
            flags=RecipeParametersFlags.TEMPERATURE_PRESENT | RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT,
            cooking_step_index=1,
            cooking_process_type=CookingProcessType.NO_COOKING,
            temperature=20.0,
            temperature_gradient=0.5,
        )
        encoded = characteristic.build_value(data)
        parsed = characteristic.parse_value(encoded)
        assert parsed.temperature == 20.0
        assert parsed.temperature_gradient == 0.5

    def test_rfu_flags_fail(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x80, 0x00, 0x01, 0x00, 0x00]))

    def test_invalid_termination_condition_fails(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x40, 0x00, 0x01, 0x00, 0x00, 0x03, 0x00]))

    def test_invalid_cooking_process_type_fails(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x00, 0x01, 0x00, 0x12]))

    def test_temperature_unknown_sentinel_raises_special_value(
        self, characteristic: RecipeParametersCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x08, 0x00, 0x01, 0x00, 0x00, 0x00, 0x80]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_humidity_unknown_sentinel_raises_special_value(
        self, characteristic: RecipeParametersCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x20, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xFF]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_temperature_gradient_range_build_fails(self, characteristic: RecipeParametersCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(
                RecipeParametersData(
                    flags=RecipeParametersFlags.TEMPERATURE_PRESENT
                    | RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT,
                    cooking_step_index=1,
                    cooking_process_type=CookingProcessType.NO_COOKING,
                    temperature=20.0,
                    temperature_gradient=12.8,
                )
            )

    def test_temperature_increase_with_humidity_decrease_fails(
        self, characteristic: RecipeParametersCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x40, 0x00, 0x01, 0x00, 0x00, 0x09, 0x00]))
