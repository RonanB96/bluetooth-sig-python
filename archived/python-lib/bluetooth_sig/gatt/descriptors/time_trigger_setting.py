"""Time Trigger Setting Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class TimeTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """Time Trigger Setting descriptor data."""

    time_interval: int  # in seconds


class TimeTriggerSettingDescriptor(BaseDescriptor):
    """Time Trigger Setting Descriptor (0x290E).

    Defines time-based trigger settings for measurements.
    Contains time interval in seconds for periodic triggering.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint24"

    def _parse_descriptor_value(self, data: bytes) -> TimeTriggerSettingData:
        """Parse Time Trigger Setting value.

        Args:
            data: Raw bytes (should be 3 bytes for uint24)

        Returns:
            TimeTriggerSettingData with time interval

        Raises:
            ValueError: If data is not exactly 3 bytes
        """
        # Parse as uint24 (3 bytes)
        time_interval = DataParser.parse_int32(data + b"\x00", endian="little") & 0xFFFFFF

        return TimeTriggerSettingData(time_interval=time_interval)

    def get_time_interval(self, data: bytes) -> int:
        """Get the time interval in seconds."""
        parsed = self._parse_descriptor_value(data)
        return parsed.time_interval
