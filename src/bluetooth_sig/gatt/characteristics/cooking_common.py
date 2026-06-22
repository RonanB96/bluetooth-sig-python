"""Shared helpers and structs for Cookware and Voice Assistant characteristics."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from .utils import DataParser


def decode_cooking_temperature(raw_value: int) -> float:
    """Decode cooking temperature raw value to degrees Celsius."""
    return raw_value * 0.1


def encode_cooking_temperature(value: float) -> int:
    """Encode cooking temperature in degrees Celsius to raw sint16."""
    return round(value * 10.0)


def decode_perceived_power(raw_value: int) -> float:
    """Decode perceived power raw value to percent."""
    return raw_value * 0.1


def encode_perceived_power(value: float) -> int:
    """Encode perceived power percent to raw uint16."""
    return round(value * 10.0)


def decode_kitchen_airflow(raw_value: int) -> float:
    """Decode kitchen airflow raw value to cubic meters per second."""
    return raw_value * 0.001


def encode_kitchen_airflow(value: float) -> int:
    """Encode kitchen airflow to raw uint16."""
    return round(value * 1000.0)


def decode_relative_humidity(raw_value: int) -> float:
    """Decode relative humidity raw value to percent."""
    return raw_value * 0.01


def encode_relative_humidity(value: float) -> int:
    """Encode relative humidity percent to raw uint16."""
    return round(value * 100.0)


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
    blower_fan_speed: int | None = None
    manufacturer_specific_data: bytes = b""


def parse_cooking_conditions(data: bytearray) -> CookingConditionsData:
    """Parse a Cooking Conditions-compatible byte payload."""
    flags = CookingConditionsFlags(DataParser.parse_int16(data, 0, signed=False))
    offset = 2

    power_level = None
    if flags & CookingConditionsFlags.POWER_LEVEL_PRESENT:
        power_level_raw = DataParser.parse_int16(data, offset, signed=False)
        power_level = decode_perceived_power(power_level_raw)
        offset += 2

    temperature = None
    if flags & CookingConditionsFlags.TEMPERATURE_PRESENT:
        temperature_raw = DataParser.parse_int16(data, offset, signed=True)
        temperature = decode_cooking_temperature(temperature_raw)
        offset += 2

    humidity = None
    if flags & CookingConditionsFlags.HUMIDITY_PRESENT:
        humidity_raw = DataParser.parse_int16(data, offset, signed=False)
        humidity = decode_relative_humidity(humidity_raw)
        offset += 2

    blower_fan_speed = None
    if flags & CookingConditionsFlags.BLOWER_FAN_SPEED_PRESENT:
        blower_fan_speed = DataParser.parse_int8(data, offset, signed=False)
        offset += 1

    manufacturer_data = b""
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
    result = bytearray()
    result.extend(DataParser.encode_int16(int(value.flags), signed=False))

    if value.flags & CookingConditionsFlags.POWER_LEVEL_PRESENT:
        if value.power_level is None:
            raise ValueError("power_level is required when POWER_LEVEL_PRESENT is set")
        result.extend(DataParser.encode_int16(encode_perceived_power(value.power_level), signed=False))

    if value.flags & CookingConditionsFlags.TEMPERATURE_PRESENT:
        if value.temperature is None:
            raise ValueError("temperature is required when TEMPERATURE_PRESENT is set")
        result.extend(DataParser.encode_int16(encode_cooking_temperature(value.temperature), signed=True))

    if value.flags & CookingConditionsFlags.HUMIDITY_PRESENT:
        if value.humidity is None:
            raise ValueError("humidity is required when HUMIDITY_PRESENT is set")
        result.extend(DataParser.encode_int16(encode_relative_humidity(value.humidity), signed=False))

    if value.flags & CookingConditionsFlags.BLOWER_FAN_SPEED_PRESENT:
        if value.blower_fan_speed is None:
            raise ValueError("blower_fan_speed is required when BLOWER_FAN_SPEED_PRESENT is set")
        result.extend(DataParser.encode_int8(value.blower_fan_speed, signed=False))

    if value.flags & CookingConditionsFlags.MANUFACTURER_DATA_PRESENT:
        result.extend(value.manufacturer_specific_data)

    return result
