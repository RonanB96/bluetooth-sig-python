"""Cooking Sensor Info Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class CookingSensorInfoData(msgspec.Struct, frozen=True, kw_only=True):
    """Cooking Sensor Info descriptor data."""

    sensor_info: int


class CookingSensorInfoDescriptor(BaseDescriptor):
    """Cooking Sensor Info Descriptor (0x2916)."""

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> CookingSensorInfoData:
        sensor_info = DataParser.parse_int16(data, endian="little")
        return CookingSensorInfoData(sensor_info=sensor_info)
