"""Recipe Parameters characteristic (0x2C27)."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..constants import SIZE_UINT8, SIZE_UINT16
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cooking_common import (
    COOKING_TEMPERATURE,
    HUMIDITY,
    validate_flags,
)
from .utils import DataParser

_TEMPERATURE_GRADIENT_MIN = -12.8
_TEMPERATURE_GRADIENT_MAX = 12.7


class RecipeParametersFlags(IntFlag):
    """Recipe parameter field presence and behavior flags."""

    OVERSHOOT_PREVENTION = 1 << 0
    LAST_COOKING_STEP = 1 << 1
    USER_ACTION_REQUIRED = 1 << 2
    TEMPERATURE_PRESENT = 1 << 3
    TEMPERATURE_GRADIENT_PRESENT = 1 << 4
    HUMIDITY_PRESENT = 1 << 5
    TERMINATION_CONDITION_PRESENT = 1 << 6


class TerminationConditionFlags(IntFlag):
    """Recipe termination condition bitfield."""

    TEMPERATURE_INCREASE = 1 << 0
    TEMPERATURE_DECREASE = 1 << 1
    HUMIDITY_INCREASE = 1 << 2
    HUMIDITY_DECREASE = 1 << 3
    LOGICAL_AND = 1 << 15


class CookingProcessType(IntEnum):
    """Recipe cooking process type values from GSS."""

    NO_COOKING = 0x00
    PREHEATING = 0x01
    BAKING = 0x02
    BOILING = 0x03
    BRAISING = 0x04
    BROILING = 0x05
    COOLING = 0x06
    FREEZING = 0x07
    FRYING = 0x08
    GRILLING = 0x09
    MELTING = 0x0A
    POACHING = 0x0B
    ROASTING = 0x0C
    SAUTEING = 0x0D
    SIMMERING = 0x0E
    SOUS_VIDE = 0x0F
    STEAMING = 0x10
    STEWING = 0x11
    OTHER_UNKNOWN = 0xFF


class RecipeParametersData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Recipe Parameters payload."""

    flags: RecipeParametersFlags
    cooking_step_index: int
    cooking_process_type: CookingProcessType
    duration_seconds: int | None = None
    temperature: float | None = None
    temperature_gradient: float | None = None
    humidity: float | None = None
    termination_condition: TerminationConditionFlags | None = None


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
        validate_flags(flags, RecipeParametersFlags, "Recipe Parameters Flags")
        cooking_step_index = DataParser.parse_int16(data, 2, signed=False)
        cooking_process_type = CookingProcessType(DataParser.parse_int8(data, 4, signed=False))

        offset = 5
        duration_seconds = None
        if cooking_process_type != CookingProcessType.NO_COOKING:
            duration_seconds = DataParser.parse_int16(data, offset, signed=False)
            offset += SIZE_UINT16

        temperature = None
        if flags & RecipeParametersFlags.TEMPERATURE_PRESENT:
            temperature = COOKING_TEMPERATURE.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
            offset += SIZE_UINT16

        temperature_gradient = None
        if (
            flags & RecipeParametersFlags.TEMPERATURE_PRESENT
            and flags & RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT
        ):
            gradient_raw = DataParser.parse_int8(data, offset, signed=True)
            temperature_gradient = gradient_raw * 0.1
            # NOTE: custom validation required because this is a nested composite
            # field; the automatic YAML range validator only sees RecipeParametersData.
            if not _TEMPERATURE_GRADIENT_MIN <= temperature_gradient <= _TEMPERATURE_GRADIENT_MAX:
                raise ValueError("temperature_gradient is outside the SIG range")
            offset += SIZE_UINT8

        humidity = None
        if flags & RecipeParametersFlags.HUMIDITY_PRESENT:
            humidity = HUMIDITY.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
            offset += SIZE_UINT16

        termination_condition = None
        if flags & RecipeParametersFlags.TERMINATION_CONDITION_PRESENT:
            termination_condition = TerminationConditionFlags(DataParser.parse_int16(data, offset, signed=False))
            # NOTE: custom validation required because this nested bitfield's RFU
            # and mutual-exclusion rules are not applied by the top-level YAML parser.
            validate_flags(termination_condition, TerminationConditionFlags, "Termination Condition")
            _validate_termination_condition(termination_condition)

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
        validate_flags(data.flags, RecipeParametersFlags, "Recipe Parameters Flags")
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.cooking_step_index, signed=False))
        result.extend(DataParser.encode_int8(int(data.cooking_process_type), signed=False))

        if data.cooking_process_type != CookingProcessType.NO_COOKING:
            if data.duration_seconds is None:
                raise ValueError("duration_seconds is required when cooking_process_type is not 0")
            result.extend(DataParser.encode_int16(data.duration_seconds, signed=False))

        if data.flags & RecipeParametersFlags.TEMPERATURE_PRESENT:
            if data.temperature is None:
                raise ValueError("temperature is required when TEMPERATURE_PRESENT is set")
            result.extend(COOKING_TEMPERATURE.build_value(data.temperature))

        if (
            data.flags & RecipeParametersFlags.TEMPERATURE_PRESENT
            and data.flags & RecipeParametersFlags.TEMPERATURE_GRADIENT_PRESENT
        ):
            if data.temperature_gradient is None:
                raise ValueError("temperature_gradient is required when TEMPERATURE_GRADIENT_PRESENT is set")
            # NOTE: mirrors decode-time nested-field validation; automatic YAML
            # range validation does not inspect fields inside RecipeParametersData.
            if not _TEMPERATURE_GRADIENT_MIN <= data.temperature_gradient <= _TEMPERATURE_GRADIENT_MAX:
                raise ValueError("temperature_gradient is outside the SIG range")
            result.extend(DataParser.encode_int8(round(data.temperature_gradient * 10.0), signed=True))

        if data.flags & RecipeParametersFlags.HUMIDITY_PRESENT:
            if data.humidity is None:
                raise ValueError("humidity is required when HUMIDITY_PRESENT is set")
            result.extend(HUMIDITY.build_value(data.humidity))

        if data.flags & RecipeParametersFlags.TERMINATION_CONDITION_PRESENT:
            if data.termination_condition is None:
                raise ValueError("termination_condition is required when TERMINATION_CONDITION_PRESENT is set")
            # NOTE: mirrors decode-time nested-bitfield validation; automatic YAML
            # validation does not inspect fields inside RecipeParametersData.
            validate_flags(data.termination_condition, TerminationConditionFlags, "Termination Condition")
            _validate_termination_condition(data.termination_condition)
            result.extend(DataParser.encode_int16(int(data.termination_condition), signed=False))

        return result


def _validate_termination_condition(flags: TerminationConditionFlags) -> None:
    """Validate mutually exclusive termination condition pairs from CWS."""
    if (
        flags & TerminationConditionFlags.TEMPERATURE_INCREASE
        and flags & TerminationConditionFlags.TEMPERATURE_DECREASE
    ):
        raise ValueError("temperature increase and decrease termination conditions are mutually exclusive")
    if flags & TerminationConditionFlags.HUMIDITY_INCREASE and flags & TerminationConditionFlags.HUMIDITY_DECREASE:
        raise ValueError("humidity increase and decrease termination conditions are mutually exclusive")
    if flags & TerminationConditionFlags.TEMPERATURE_INCREASE and flags & TerminationConditionFlags.HUMIDITY_DECREASE:
        raise ValueError("humidity decrease condition can only be set when temperature increase is cleared")
