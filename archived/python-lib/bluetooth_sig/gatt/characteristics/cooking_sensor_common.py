"""Shared typed sensor-value formats for Cookware Service sensor payloads."""

from __future__ import annotations

from typing import ClassVar

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

from ..constants import SIZE_UINT16, SIZE_UINT32
from .base import BaseCharacteristic
from .cooking_common import COOKING_TEMPERATURE, HUMIDITY
from .pressure import PressureCharacteristic

_PRESSURE = PressureCharacteristic()


class CookingSensorValue(msgspec.Struct, frozen=True, kw_only=True):
    """Typed sensor value selected by a Cooking Sensor Info UUID."""

    sensor_uuid: BluetoothUUID
    value: float


class CookingSensorDataFormat(msgspec.Struct, frozen=True, kw_only=True):
    """Permitted Cookware Sensor Data format from Assigned Numbers."""

    characteristic: BaseCharacteristic[float]
    value_size: int


class CookingSensorFormats:
    """Permitted sensor data formats for CWS."""

    formats: ClassVar[dict[BluetoothUUID, CookingSensorDataFormat]] = {
        COOKING_TEMPERATURE.uuid: CookingSensorDataFormat(characteristic=COOKING_TEMPERATURE, value_size=SIZE_UINT16),
        HUMIDITY.uuid: CookingSensorDataFormat(characteristic=HUMIDITY, value_size=SIZE_UINT16),
        _PRESSURE.uuid: CookingSensorDataFormat(characteristic=_PRESSURE, value_size=SIZE_UINT32),
    }

    @classmethod
    def get(cls, sensor_uuid: BluetoothUUID) -> CookingSensorDataFormat:
        """Return the permitted format for a Cooking Sensor Info UUID."""
        sensor_format = cls.formats.get(sensor_uuid)
        if sensor_format is None:
            raise ValueError("Cooking Sensor Info UUID is not permitted for Cookware Sensor Data")
        return sensor_format


def parse_cooking_sensor_value(sensor_uuid: BluetoothUUID, data: bytes | bytearray) -> CookingSensorValue:
    """Parse a CWS sensor value using the format selected by the sensor UUID."""
    sensor_format = CookingSensorFormats.get(sensor_uuid)
    if len(data) != sensor_format.value_size:
        raise ValueError(
            f"Sensor Data for UUID {sensor_uuid.short_form} must be {sensor_format.value_size} octets, got {len(data)}"
        )
    return CookingSensorValue(
        sensor_uuid=sensor_uuid,
        value=sensor_format.characteristic.parse_value(bytearray(data)),
    )


def encode_cooking_sensor_value(sensor_value: CookingSensorValue) -> bytearray:
    """Encode a CWS sensor value using the format selected by its UUID."""
    sensor_format = CookingSensorFormats.get(sensor_value.sensor_uuid)
    return sensor_format.characteristic.build_value(sensor_value.value)
