"""IMD Trigger Setting Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class IMDTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """IMD Trigger Setting descriptor data."""

    trigger_setting: int


class IMDTriggerSettingDescriptor(BaseDescriptor):
    """IMD Trigger Setting Descriptor (0x2915).

    Defines trigger settings for Impedance Measurement Devices (IMD).
    Contains trigger configuration for IMD measurements.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> IMDTriggerSettingData:
        """Parse IMD Trigger Setting value.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            IMDTriggerSettingData with trigger setting

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"IMD Trigger Setting data must be exactly 2 bytes, got {len(data)}")

        trigger_setting = DataParser.parse_int16(data, endian="little")

        return IMDTriggerSettingData(trigger_setting=trigger_setting)

    def get_trigger_setting(self, data: bytes) -> int:
        """Get the IMD trigger setting."""
        parsed = self._parse_descriptor_value(data)
        return parsed.trigger_setting
