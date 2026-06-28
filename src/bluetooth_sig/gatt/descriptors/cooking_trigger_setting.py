"""Cooking Trigger Setting Descriptor implementation."""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

from ..characteristics.cooking_sensor_common import CookingSensorValue, parse_cooking_sensor_value
from ..characteristics.utils import DataParser
from ..constants import SIZE_UINT16
from .base import BaseDescriptor

_INTERVAL_SIZE = SIZE_UINT16


class CookingTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """Cooking Trigger Setting descriptor data."""

    interval_100ms: int
    delta: CookingSensorValue


class CookingTriggerSettingDescriptor(BaseDescriptor):
    """Cooking Trigger Setting Descriptor (0x2917)."""

    _writable = True

    def __init__(self, sensor_uuid: BluetoothUUID | None = None) -> None:
        """Initialize descriptor with the associated Cooking Sensor Info UUID."""
        self.sensor_uuid = sensor_uuid
        super().__init__()

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> CookingTriggerSettingData:
        minimum_length = _INTERVAL_SIZE
        if len(data) < minimum_length:
            raise ValueError(
                f"Cooking Trigger Settings descriptor needs at least {minimum_length} bytes, got {len(data)}"
            )
        interval_100ms = DataParser.parse_int16(data, 0, signed=False, endian="little")
        if self.sensor_uuid is None:
            raise ValueError("Cooking Sensor Info UUID is required to decode Trigger Setting Delta")
        return CookingTriggerSettingData(
            interval_100ms=interval_100ms,
            delta=parse_cooking_sensor_value(self.sensor_uuid, data[_INTERVAL_SIZE:]),
        )
