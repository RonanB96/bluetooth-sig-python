"""Environmental Sensing Trigger Setting Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class EnvironmentalSensingTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """Environmental Sensing Trigger Setting descriptor data."""

    condition: int
    operand: int


class EnvironmentalSensingTriggerSettingDescriptor(BaseDescriptor):
    """Environmental Sensing Trigger Setting Descriptor (0x290D).

    Defines trigger conditions for environmental sensing measurements.
    Contains condition and operand for triggering measurements.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> EnvironmentalSensingTriggerSettingData:
        """Parse Environmental Sensing Trigger Setting value.

        Format: 3 bytes
        - Condition (1 byte)
        - Operand (2 bytes, uint16)

        Args:
            data: Raw bytes (should be 3 bytes)

        Returns:
            EnvironmentalSensingTriggerSettingData with condition and operand

        Raises:
            ValueError: If data is not exactly 3 bytes
        """
        if len(data) != 3:
            raise ValueError(f"Environmental Sensing Trigger Setting data must be exactly 3 bytes, got {len(data)}")

        return EnvironmentalSensingTriggerSettingData(
            condition=DataParser.parse_int8(data, offset=0),
            operand=DataParser.parse_int16(data, offset=1, endian="little"),
        )

    def get_condition(self, data: bytes) -> int:
        """Get the trigger condition."""
        parsed = self._parse_descriptor_value(data)
        return parsed.condition

    def get_operand(self, data: bytes) -> int:
        """Get the trigger operand."""
        parsed = self._parse_descriptor_value(data)
        return parsed.operand
