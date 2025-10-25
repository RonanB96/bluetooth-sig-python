"""Value Trigger Setting Descriptor implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class TriggerCondition(IntEnum):
    """Trigger condition values for Value Trigger Setting."""

    NONE = 0x00
    EQUAL_TO = 0x01
    NOT_EQUAL_TO = 0x02
    LESS_THAN = 0x03
    LESS_THAN_OR_EQUAL_TO = 0x04
    GREATER_THAN = 0x05
    GREATER_THAN_OR_EQUAL_TO = 0x06


class ValueTriggerSettingData(msgspec.Struct, frozen=True, kw_only=True):
    """Value Trigger Setting descriptor data."""

    condition: int
    value: int  # This would typically be the same format as the characteristic value


class ValueTriggerSettingDescriptor(BaseDescriptor):
    """Value Trigger Setting Descriptor (0x290A).

    Defines trigger conditions for value-based notifications.
    Contains condition and reference value for triggering.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ValueTriggerSettingData:
        """Parse Value Trigger Setting value.

        Format depends on the characteristic's value format.
        Basic implementation assumes: condition (1 byte) + value (same as characteristic).

        Args:
            data: Raw bytes containing condition and value

        Returns:
            ValueTriggerSettingData with condition and value

        Raises:
            ValueError: If data is too short
        """
        if len(data) < 2:
            raise ValueError(f"Value Trigger Setting data must be at least 2 bytes, got {len(data)}")

        condition = DataParser.parse_int8(data, offset=0)

        # For simplicity, assume the value is a uint8 following the condition
        # In practice, this should match the characteristic's value format
        value = DataParser.parse_int8(data, offset=1)

        return ValueTriggerSettingData(
            condition=condition,
            value=value,
        )

    def get_condition(self, data: bytes) -> int:
        """Get the trigger condition."""
        parsed = self._parse_descriptor_value(data)
        return parsed.condition

    def get_trigger_value(self, data: bytes) -> int:
        """Get the trigger reference value."""
        parsed = self._parse_descriptor_value(data)
        return parsed.value

    def is_condition_equal_to(self, data: bytes) -> bool:
        """Check if condition is 'equal to'."""
        return self.get_condition(data) == TriggerCondition.EQUAL_TO

    def is_condition_greater_than(self, data: bytes) -> bool:
        """Check if condition is 'greater than'."""
        return self.get_condition(data) == TriggerCondition.GREATER_THAN
