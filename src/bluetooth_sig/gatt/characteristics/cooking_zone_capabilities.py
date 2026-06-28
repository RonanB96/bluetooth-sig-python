"""Cooking Zone Capabilities characteristic (0x2C29)."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..constants import SIZE_UINT8, SIZE_UINT16, SIZE_UINT24
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cooking_common import (
    COOKING_TEMPERATURE,
    COOKING_ZONE_PERCEIVED_POWER,
    KITCHEN_APPLIANCE_AIRFLOW,
    POWER,
    validate_flags,
)
from .utils import DataParser


class CookingZoneCapabilitiesFlags(IntFlag):
    """Bit flags for supported zone capability fields."""

    AGGREGATION_SUPPORTED = 1 << 0
    POWER_CONTROL_SUPPORTED = 1 << 1
    TEMPERATURE_CONTROL_SUPPORTED = 1 << 2
    HUMIDITY_CONTROL_SUPPORTED = 1 << 3
    BLOWER_FAN_AIRFLOW_SUPPORTED = 1 << 4
    MANUFACTURER_SPECIFIC_CONTROL_SUPPORTED = 1 << 5


class PowerTechnology(IntEnum):
    """Power technology for the cooking zone."""

    UNKNOWN_OR_OTHER = 0x00
    HEATING_INDUCTION = 0x01
    HEATING_GAS = 0x02
    HEATING_RADIANT = 0x03
    COOLING_REFRIGERATION = 0x04
    COOLING_FREEZER = 0x05
    MANUFACTURER_SPECIFIC = 0xFF


class CookingZoneCapabilitiesData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cooking Zone Capabilities payload."""

    flags: CookingZoneCapabilitiesFlags
    power_technology: PowerTechnology
    number_of_cooking_steps: int
    nominal_power: float | None = None
    boost_level_percent: int | None = None
    minimum_available_power: float | None = None
    maximum_temperature: float | None = None
    minimum_temperature: float | None = None
    maximum_blower_fan_airflow: float | None = None


class CookingZoneCapabilitiesCharacteristic(BaseCharacteristic[CookingZoneCapabilitiesData]):
    """Cooking Zone Capabilities characteristic (0x2C29).

    org.bluetooth.characteristic.cooking_zone_capabilities
    """

    min_length = 5
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookingZoneCapabilitiesData:
        flags = CookingZoneCapabilitiesFlags(DataParser.parse_int16(data, 0, signed=False))
        validate_flags(flags, CookingZoneCapabilitiesFlags, "Cooking Zone Capabilities Flags")
        power_technology = PowerTechnology(DataParser.parse_int8(data, 2, signed=False))
        number_of_cooking_steps = DataParser.parse_int16(data, 3, signed=False)

        offset = 5
        nominal_power = None
        boost_level_percent = None
        minimum_available_power = None
        if flags & CookingZoneCapabilitiesFlags.POWER_CONTROL_SUPPORTED:
            nominal_power = POWER.parse_value(bytearray(data[offset : offset + SIZE_UINT24]))
            offset += SIZE_UINT24
            boost_level_percent = DataParser.parse_int8(data, offset, signed=False)
            offset += SIZE_UINT8
            minimum_available_power = COOKING_ZONE_PERCEIVED_POWER.parse_value(
                bytearray(data[offset : offset + SIZE_UINT16])
            )
            offset += SIZE_UINT16

        maximum_temperature = None
        minimum_temperature = None
        if flags & CookingZoneCapabilitiesFlags.TEMPERATURE_CONTROL_SUPPORTED:
            maximum_temperature = COOKING_TEMPERATURE.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
            offset += SIZE_UINT16
            minimum_temperature = COOKING_TEMPERATURE.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
            offset += SIZE_UINT16

        maximum_blower_fan_airflow = None
        if flags & CookingZoneCapabilitiesFlags.BLOWER_FAN_AIRFLOW_SUPPORTED:
            maximum_blower_fan_airflow = KITCHEN_APPLIANCE_AIRFLOW.parse_value(
                bytearray(data[offset : offset + SIZE_UINT16])
            )

        return CookingZoneCapabilitiesData(
            flags=flags,
            power_technology=power_technology,
            number_of_cooking_steps=number_of_cooking_steps,
            nominal_power=nominal_power,
            boost_level_percent=boost_level_percent,
            minimum_available_power=minimum_available_power,
            maximum_temperature=maximum_temperature,
            minimum_temperature=minimum_temperature,
            maximum_blower_fan_airflow=maximum_blower_fan_airflow,
        )

    def _encode_value(self, data: CookingZoneCapabilitiesData) -> bytearray:
        validate_flags(data.flags, CookingZoneCapabilitiesFlags, "Cooking Zone Capabilities Flags")
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.flags), signed=False))
        result.extend(DataParser.encode_int8(data.power_technology, signed=False))
        result.extend(DataParser.encode_int16(data.number_of_cooking_steps, signed=False))

        if data.flags & CookingZoneCapabilitiesFlags.POWER_CONTROL_SUPPORTED:
            if data.nominal_power is None or data.boost_level_percent is None or data.minimum_available_power is None:
                raise ValueError("power control fields are required when POWER_CONTROL_SUPPORTED is set")
            result.extend(POWER.build_value(data.nominal_power))
            result.extend(DataParser.encode_int8(data.boost_level_percent, signed=False))
            result.extend(COOKING_ZONE_PERCEIVED_POWER.build_value(data.minimum_available_power))

        if data.flags & CookingZoneCapabilitiesFlags.TEMPERATURE_CONTROL_SUPPORTED:
            if data.maximum_temperature is None or data.minimum_temperature is None:
                raise ValueError("temperature fields are required when TEMPERATURE_CONTROL_SUPPORTED is set")
            result.extend(COOKING_TEMPERATURE.build_value(data.maximum_temperature))
            result.extend(COOKING_TEMPERATURE.build_value(data.minimum_temperature))

        if data.flags & CookingZoneCapabilitiesFlags.BLOWER_FAN_AIRFLOW_SUPPORTED:
            if data.maximum_blower_fan_airflow is None:
                raise ValueError("maximum_blower_fan_airflow is required when BLOWER_FAN_AIRFLOW_SUPPORTED is set")
            result.extend(KITCHEN_APPLIANCE_AIRFLOW.build_value(data.maximum_blower_fan_airflow))

        return result
