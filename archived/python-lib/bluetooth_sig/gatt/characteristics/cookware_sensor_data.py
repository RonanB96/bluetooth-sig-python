"""Cookware Sensor Data characteristic (0x2C2C)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SIZE_UINT8
from ..context import CharacteristicContext
from ..descriptor_utils import get_descriptor_from_context
from ..descriptors.cooking_sensor_info import CookingSensorInfoData, CookingSensorInfoDescriptor
from .base import BaseCharacteristic
from .cooking_common import validate_flags
from .cooking_sensor_common import CookingSensorValue, encode_cooking_sensor_value, parse_cooking_sensor_value
from .utils import DataParser


class CookwareSensorStatus(IntFlag):
    """Cookware Sensor Data status bits."""

    NO_ERROR = 0
    MEASURED_VALUE_OUT_OF_RANGE = 1 << 0
    SENSOR_INTERNAL_ERROR = 1 << 1


class CookwareSensorDataValue(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cookware Sensor Data payload.

    The sensor data field's type is determined by the Cooking Sensor Info
    descriptor UUID for the specific sensor instance.
    """

    sensor_status: CookwareSensorStatus
    sensor_data: CookingSensorValue


class CookwareSensorDataCharacteristic(BaseCharacteristic[CookwareSensorDataValue]):
    """Cookware Sensor Data characteristic (0x2C2C).

    org.bluetooth.characteristic.cookware_sensor_data
    """

    min_length = SIZE_UINT8
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookwareSensorDataValue:
        sensor_status = CookwareSensorStatus(DataParser.parse_int8(data, 0, signed=False))
        validate_flags(sensor_status, CookwareSensorStatus, "Sensor Status")
        sensor_data = bytearray(data[SIZE_UINT8:])
        sensor_info = _get_sensor_info(ctx)
        if sensor_info is None:
            raise ValueError("Cooking Sensor Info descriptor is required to decode Sensor Data")
        return CookwareSensorDataValue(
            sensor_status=sensor_status,
            sensor_data=parse_cooking_sensor_value(sensor_info.sensor_uuid, sensor_data),
        )

    def _encode_value(self, data: CookwareSensorDataValue) -> bytearray:
        validate_flags(data.sensor_status, CookwareSensorStatus, "Sensor Status")
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.sensor_status), signed=False))
        result.extend(encode_cooking_sensor_value(data.sensor_data))
        return result


def _get_sensor_info(ctx: CharacteristicContext | None) -> CookingSensorInfoData | None:
    """Return Cooking Sensor Info descriptor data from parse context, if present."""
    descriptor_data = get_descriptor_from_context(ctx, CookingSensorInfoDescriptor)
    if descriptor_data is None or not descriptor_data.parse_success:
        return None
    if isinstance(descriptor_data.value, CookingSensorInfoData):
        return descriptor_data.value
    raise ValueError("Cooking Sensor Info descriptor has unexpected value type")
