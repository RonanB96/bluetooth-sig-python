"""Shared helpers and structs for Cooking/Cookware characteristics."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SIZE_UINT8, SIZE_UINT16
from .cooking_temperature import CookingTemperatureCharacteristic
from .cooking_zone_perceived_power import CookingZonePerceivedPowerCharacteristic
from .humidity import HumidityCharacteristic
from .kitchen_appliance_airflow import KitchenApplianceAirflowCharacteristic
from .percentage_8 import Percentage8Characteristic
from .power import PowerCharacteristic
from .utils import DataParser

COOKING_TEMPERATURE = CookingTemperatureCharacteristic()
COOKING_ZONE_PERCEIVED_POWER = CookingZonePerceivedPowerCharacteristic()
HUMIDITY = HumidityCharacteristic()
KITCHEN_APPLIANCE_AIRFLOW = KitchenApplianceAirflowCharacteristic()
PERCENTAGE_8 = Percentage8Characteristic()
POWER = PowerCharacteristic()


class CookingConditionsFlags(IntFlag):
    """Bit flags for Cooking Conditions payload presence."""

    POWER_LEVEL_PRESENT = 1 << 0
    TEMPERATURE_PRESENT = 1 << 1
    HUMIDITY_PRESENT = 1 << 2
    BLOWER_FAN_SPEED_PRESENT = 1 << 3
    MANUFACTURER_DATA_PRESENT = 1 << 4


class CookingConditionsData(msgspec.Struct, frozen=True, kw_only=True):
    """Shared parsed data model for Cooking Conditions characteristics."""

    flags: CookingConditionsFlags
    power_level: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    blower_fan_speed: float | None = None
    manufacturer_specific_data: bytes | None = None


def parse_cooking_conditions(data: bytearray) -> CookingConditionsData:
    """Parse a Cooking Conditions-compatible byte payload."""
    flags = CookingConditionsFlags(DataParser.parse_int16(data, 0, signed=False))
    validate_flags(flags, CookingConditionsFlags, "Cooking Conditions Flags")
    offset = 2

    power_level = None
    if flags & CookingConditionsFlags.POWER_LEVEL_PRESENT:
        power_level = COOKING_ZONE_PERCEIVED_POWER.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
        offset += SIZE_UINT16

    temperature = None
    if flags & CookingConditionsFlags.TEMPERATURE_PRESENT:
        temperature = COOKING_TEMPERATURE.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
        offset += SIZE_UINT16

    humidity = None
    if flags & CookingConditionsFlags.HUMIDITY_PRESENT:
        humidity = HUMIDITY.parse_value(bytearray(data[offset : offset + SIZE_UINT16]))
        offset += SIZE_UINT16

    blower_fan_speed = None
    if flags & CookingConditionsFlags.BLOWER_FAN_SPEED_PRESENT:
        blower_fan_speed = PERCENTAGE_8.parse_value(bytearray(data[offset : offset + SIZE_UINT8]))
        offset += SIZE_UINT8

    manufacturer_data = None
    if flags & CookingConditionsFlags.MANUFACTURER_DATA_PRESENT:
        manufacturer_data = bytes(data[offset:])

    return CookingConditionsData(
        flags=flags,
        power_level=power_level,
        temperature=temperature,
        humidity=humidity,
        blower_fan_speed=blower_fan_speed,
        manufacturer_specific_data=manufacturer_data,
    )


def encode_cooking_conditions(value: CookingConditionsData) -> bytearray:
    """Encode shared Cooking Conditions data model into bytes."""
    validate_flags(value.flags, CookingConditionsFlags, "Cooking Conditions Flags")
    result = bytearray()
    result.extend(DataParser.encode_int16(int(value.flags), signed=False))

    if value.flags & CookingConditionsFlags.POWER_LEVEL_PRESENT:
        if value.power_level is None:
            raise ValueError("power_level is required when POWER_LEVEL_PRESENT is set")
        result.extend(COOKING_ZONE_PERCEIVED_POWER.build_value(value.power_level))

    if value.flags & CookingConditionsFlags.TEMPERATURE_PRESENT:
        if value.temperature is None:
            raise ValueError("temperature is required when TEMPERATURE_PRESENT is set")
        result.extend(COOKING_TEMPERATURE.build_value(value.temperature))

    if value.flags & CookingConditionsFlags.HUMIDITY_PRESENT:
        if value.humidity is None:
            raise ValueError("humidity is required when HUMIDITY_PRESENT is set")
        result.extend(HUMIDITY.build_value(value.humidity))

    if value.flags & CookingConditionsFlags.BLOWER_FAN_SPEED_PRESENT:
        if value.blower_fan_speed is None:
            raise ValueError("blower_fan_speed is required when BLOWER_FAN_SPEED_PRESENT is set")
        result.extend(PERCENTAGE_8.build_value(value.blower_fan_speed))

    if value.flags & CookingConditionsFlags.MANUFACTURER_DATA_PRESENT:
        if value.manufacturer_specific_data is None:
            raise ValueError("manufacturer_specific_data is required when MANUFACTURER_DATA_PRESENT is set")
        result.extend(value.manufacturer_specific_data)

    return result


def validate_flags(flags: IntFlag, flag_type: type[IntFlag], field_name: str) -> None:
    """Reject RFU bits for manually parsed IntFlag fields."""
    valid_mask = 0
    for member in flag_type:
        valid_mask |= int(member)
    if int(flags) & ~valid_mask:
        raise ValueError(f"{field_name} contains reserved bits")
