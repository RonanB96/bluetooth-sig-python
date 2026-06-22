"""Cooking Trigger Setting Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class CookingTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """Cooking Trigger Setting descriptor data."""

    trigger_setting: int


class CookingTriggerSettingDescriptor(BaseDescriptor):
    """Cooking Trigger Setting Descriptor (0x2917)."""

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> CookingTriggerSettingData:
        trigger_setting = DataParser.parse_int16(data, endian="little")
        return CookingTriggerSettingData(trigger_setting=trigger_setting)
