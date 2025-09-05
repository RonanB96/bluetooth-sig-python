"""Base class for GATT characteristics."""

from __future__ import annotations

import re
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..uuid_registry import uuid_registry


@dataclass
class BaseCharacteristic(ABC):
    """Base class for all GATT characteristics.

    Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML specifications.
    Supports manual overrides via _manual_unit and _manual_value_type attributes.
    """

    # Instance variables
    uuid: str
    properties: set[str] = field(default_factory=set)
    value_type: str = field(default="string")

    def __post_init__(self):
        """Initialize characteristic with UUID from registry based on class name."""
        if not hasattr(self, "_char_uuid"):
            # First try explicit characteristic name if set
            if hasattr(self, "_characteristic_name") and self._characteristic_name:
                char_info = uuid_registry.get_characteristic_info(
                    self._characteristic_name
                )
                if char_info:
                    self._char_uuid = char_info.uuid
                    # Set value_type from registry if available and not manually overridden
                    if not hasattr(self, "_manual_value_type") and char_info.value_type:
                        self.value_type = char_info.value_type
                    return

            # Convert class name to standard format and try all possibilities
            name = self.__class__.__name__

            # Try different name formats like services do:
            # 1. Full class name (e.g., BatteryLevelCharacteristic)
            # 2. Without 'Characteristic' suffix (e.g., BatteryLevel)
            # 3. Space-separated (e.g., Battery Level)
            char_name = name
            if name.endswith("Characteristic"):
                char_name = name[:-14]  # Remove 'Characteristic' suffix

            # Split on camelCase and convert to space-separated
            words = re.findall("[A-Z][^A-Z]*", char_name)
            display_name = " ".join(words)

            # Try different name formats
            org_name = "org.bluetooth.characteristic." + "_".join(
                word.lower() for word in words
            )
            names_to_try = [
                name,  # Full class name (e.g. BatteryLevelCharacteristic)
                char_name,  # Without 'Characteristic' suffix
                display_name,  # Space-separated (e.g. Battery Level)
                org_name,  # Characteristic-specific format
            ]

            # Try each name format
            for try_name in names_to_try:
                char_info = uuid_registry.get_characteristic_info(try_name)
                if char_info:
                    self._char_uuid = char_info.uuid
                    # Set value_type from registry if available and not manually overridden
                    if not hasattr(self, "_manual_value_type") and char_info.value_type:
                        self.value_type = char_info.value_type
                    break
            else:
                raise ValueError(f"No UUID found for characteristic: {name}")

    @property
    def char_uuid(self) -> str:
        """Get the characteristic UUID from registry based on name."""
        return getattr(self, "_char_uuid", "")

    @property
    def name(self) -> str:
        """Get the characteristic name from UUID registry."""
        if hasattr(self, "_characteristic_name"):
            return self._characteristic_name
        info = uuid_registry.get_characteristic_info(self.char_uuid)
        return info.name if info else f"Unknown Characteristic ({self.char_uuid})"

    @property
    def summary(self) -> str:
        """Get the characteristic summary."""
        info = uuid_registry.get_characteristic_info(self.char_uuid)
        return info.summary if info else ""

    @classmethod
    def matches_uuid(cls, uuid: str) -> bool:
        """Check if this characteristic matches the given UUID."""
        # Create a temporary instance to get the UUID
        try:
            temp_instance = cls(uuid="", properties=set())
            return temp_instance.char_uuid.lower() in uuid.lower()
        except (ValueError, AttributeError):
            return False

    @abstractmethod
    def parse_value(self, data: bytearray) -> Any:
        """Parse the characteristic's raw value.

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Parsed value in the appropriate type

        Raises:
            NotImplementedError: This is an abstract method
        """
        raise NotImplementedError

    @property
    def unit(self) -> str:
        """Get the unit of measurement for this characteristic.

        First tries manual unit override, then falls back to YAML registry.
        This allows manual overrides to take precedence while using automatic parsing as default.
        """
        # First try manual unit override (takes priority)
        if hasattr(self, "_manual_unit"):
            return self._manual_unit

        # Fallback to unit from YAML registry for automatic parsing
        char_info = uuid_registry.get_characteristic_info(self.char_uuid)
        if char_info and char_info.unit:
            return char_info.unit

        return ""

    @property
    def parsed_value_type(self) -> str:
        """Get the value type for this characteristic.

        First tries manual value_type override, then falls back to YAML registry.
        This allows manual overrides to take precedence while using automatic parsing as default.
        """
        # First try manual value_type override (takes priority)
        if hasattr(self, "_manual_value_type"):
            return self._manual_value_type

        # Fallback to value_type from YAML registry for automatic parsing
        char_info = uuid_registry.get_characteristic_info(self.char_uuid)
        if char_info and char_info.value_type:
            return char_info.value_type

        # Final fallback to instance value_type
        return self.value_type

    def _parse_ieee11073_sfloat(self, sfloat_val: int) -> float:
        """Convert IEEE-11073 16-bit SFLOAT to Python float.

        This is a common pattern used in health device characteristics
        like blood pressure, pulse oximetry, and temperature measurements.

        Args:
            sfloat_val: 16-bit SFLOAT value as integer

        Returns:
            Converted float value
        """
        if sfloat_val == 0x07FF:  # NaN
            return float("nan")
        if sfloat_val == 0x0800:  # NRes (Not a valid result)
            return float("nan")
        if sfloat_val == 0x07FE:  # +INFINITY
            return float("inf")
        if sfloat_val == 0x0802:  # -INFINITY
            return float("-inf")

        # Extract mantissa and exponent
        mantissa = sfloat_val & 0x0FFF
        exponent = (sfloat_val >> 12) & 0x0F

        # Handle negative mantissa
        if mantissa & 0x0800:
            mantissa = mantissa - 0x1000

        # Handle negative exponent
        if exponent & 0x08:
            exponent = exponent - 0x10

        return mantissa * (10**exponent)

    def _parse_ieee11073_timestamp(
        self, data: bytearray, offset: int
    ) -> dict[str, int]:
        """Parse IEEE-11073 timestamp format (7 bytes).

        This is a common pattern used in health device characteristics
        for parsing timestamps.

        Args:
            data: Raw bytearray containing the timestamp
            offset: Offset where timestamp starts

        Returns:
            Dictionary with timestamp components

        Raises:
            ValueError: If not enough data for timestamp
        """
        if len(data) < offset + 7:
            raise ValueError("Not enough data for timestamp parsing")

        timestamp_data = data[offset : offset + 7]
        year, month, day, hours, minutes, seconds = struct.unpack(
            "<HBBBBB", timestamp_data
        )
        return {
            "year": year,
            "month": month,
            "day": day,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        }

    def _parse_utf8_string(self, data: bytearray) -> str:
        """Parse UTF-8 string from bytearray.

        This is a common pattern used in device info and generic access
        characteristics for parsing string values.

        Args:
            data: Raw bytearray containing string data

        Returns:
            Decoded UTF-8 string with null bytes stripped
        """
        return data.decode("utf-8", errors="replace").rstrip("\x00")
