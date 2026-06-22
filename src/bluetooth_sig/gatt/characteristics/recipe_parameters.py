"""Recipe Parameters characteristic (0x2C27)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cooking_common import (
    decode_cooking_temperature,
    decode_relative_humidity,
    encode_cooking_temperature,
    encode_relative_humidity,
)
from .utils import DataParser


class RecipeParametersFlags(IntFlag):
    """Recipe parameter field presence and behavior flags."""

    OVERSHOOT_PREVENTION = 1 << 0
    LAST_COOKING_STEP = 1 << 1
    USER_ACTION_REQUIRED = 1 << 2
    TEMPERATURE_PRESENT = 1 << 3
    TEMPERATURE_GRADIENT_PRESENT = 1 << 4
    HUMIDITY_PRESENT = 1 << 5
    TERMINATION_CONDITION_PRESENT = 1 << 6


class RecipeParametersData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Recipe Parameters payload."""

    flags: RecipeParametersFlags
    cooking_step_index: int
    cooking_process_type: int
    duration_seconds: int | None = None
    temperature: float | None = None
    temperature_gradient: float | None = None
    humidity: float | None = None
    termination_condition: int | None = None


class RecipeParametersCharacteristic(BaseCharacteristic[RecipeParametersData]):
    """Recipe Parameters characteristic (0x2C27).

    org.bluetooth.characteristic.recipe_parameters
    """

    min_length = 5
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RecipeParametersData:
        flags = RecipeParametersFlags(DataParser.parse_int16(data, 0, signed=False))
        cooking_step_index = DataParser.parse_int16(data, 2, signed=False)
        cooking_process_type = DataParser.parse_int8(data, 4, signed=False)

        offset = 5
        duration_seconds = None
        if cooking_process_type != 0:
            duration_seconds = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        temperature = None
        if flags & RecipeParametersFlags.TEMPERATURE_PRESENT:
            temperature = decode_cooking_temperature(DataParser.parse_int16(data, offset, signed=True))
            offset += 2

        temperature_gradient = None
        if (
            flags & RecipeParametersFlags.TEMPERATURE_PRESENT
            and flags & RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT
        ):
            gradient_raw = DataParser.parse_int8(data, offset, signed=True)
            temperature_gradient = gradient_raw * 0.1
            offset += 1

        humidity = None
        if flags & RecipeParametersFlags.HUMIDITY_PRESENT:
            humidity = decode_relative_humidity(DataParser.parse_int16(data, offset, signed=False))
            offset += 2

        termination_condition = None
        if flags & RecipeParametersFlags.TERMINATION_CONDITION_PRESENT:
            termination_condition = DataParser.parse_int16(data, offset, signed=False)

        return RecipeParametersData(
            flags=flags,
            cooking_step_index=cooking_step_index,
            cooking_process_type=cooking_process_type,
            duration_seconds=duration_seconds,
            temperature=temperature,
            temperature_gradient=temperature_gradient,
            humidity=humidity,
            termination_condition=termination_condition,
        )

    def _encode_value(self, data: RecipeParametersData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.cooking_step_index, signed=False))
        result.extend(DataParser.encode_int8(data.cooking_process_type, signed=False))

        if data.cooking_process_type != 0:
            if data.duration_seconds is None:
                raise ValueError("duration_seconds is required when cooking_process_type is not 0")
            result.extend(DataParser.encode_int16(data.duration_seconds, signed=False))

        if data.flags & RecipeParametersFlags.TEMPERATURE_PRESENT:
            if data.temperature is None:
                raise ValueError("temperature is required when TEMPERATURE_PRESENT is set")
            result.extend(DataParser.encode_int16(encode_cooking_temperature(data.temperature), signed=True))

        if (
            data.flags & RecipeParametersFlags.TEMPERATURE_PRESENT
            and data.flags & RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT
        ):
            if data.temperature_gradient is None:
                raise ValueError("temperature_gradient is required when TEMPERATURE_GRADIENT_PRESENT is set")
            result.extend(DataParser.encode_int8(round(data.temperature_gradient * 10.0), signed=True))

        if data.flags & RecipeParametersFlags.HUMIDITY_PRESENT:
            if data.humidity is None:
                raise ValueError("humidity is required when HUMIDITY_PRESENT is set")
            result.extend(DataParser.encode_int16(encode_relative_humidity(data.humidity), signed=False))

        if data.flags & RecipeParametersFlags.TERMINATION_CONDITION_PRESENT:
            if data.termination_condition is None:
                raise ValueError("termination_condition is required when TERMINATION_CONDITION_PRESENT is set")
            result.extend(DataParser.encode_int16(data.termination_condition, signed=False))

        return result
