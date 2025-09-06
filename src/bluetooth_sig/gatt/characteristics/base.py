"""Base class for GATT characteristics."""

from __future__ import annotations

import re
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ...registry.yaml_cross_reference import yaml_cross_reference
from ..uuid_registry import uuid_registry

_yaml_cross_reference_available = yaml_cross_reference is not None


@dataclass
class BaseCharacteristic(ABC):  # pylint: disable=too-many-instance-attributes
    """Base class for all GATT characteristics.

    Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML specifications.
    Supports manual overrides via _manual_unit and _manual_value_type attributes.
    """

    # Instance variables
    uuid: str
    properties: set[str] = field(default_factory=set)
    value_type: str = field(default="string")

    def __post_init__(self):
        """Initialize characteristic with UUID from registry based on class name.

        Automatically resolves metadata from cross-file YAML references
        including UUIDs, data types, field sizes, unit symbols, and byte order hints.
        """
        if not hasattr(self, "_char_uuid"):
            # Try cross-file resolution first
            if _yaml_cross_reference_available:
                yaml_spec = self._resolve_yaml_spec()
                if yaml_spec:
                    self._char_uuid = yaml_spec.uuid

                    # Set additional metadata from YAML
                    if not hasattr(self, "_manual_value_type") and yaml_spec.data_type:
                        # Map GSS data types to our value types
                        type_mapping = {
                            "sint8": "int",
                            "uint8": "int",
                            "sint16": "int",
                            "uint16": "int",
                            "uint24": "int",
                            "sint32": "int",
                            "uint32": "int",
                            "float32": "float",
                            "float64": "float",
                            "utf8s": "string",
                        }
                        self.value_type = type_mapping.get(yaml_spec.data_type, "bytes")

                    # Store metadata for implementation methods
                    self._yaml_data_type = yaml_spec.data_type
                    self._yaml_field_size = yaml_spec.field_size
                    self._yaml_unit_symbol = yaml_spec.unit_symbol
                    self._yaml_unit_id = yaml_spec.unit_id
                    self._yaml_resolution_text = yaml_spec.resolution_text

                    return

            # Fallback to original registry resolution
            self._resolve_from_basic_registry()

    def _resolve_yaml_spec(self):
        """Resolve specification using YAML cross-reference system."""
        if not _yaml_cross_reference_available:
            return None

        # First try explicit characteristic name if set
        characteristic_name = getattr(self, "_characteristic_name", None)
        if characteristic_name:
            return yaml_cross_reference.resolve_characteristic_spec(characteristic_name)

        # Convert class name to standard format and try all possibilities
        name = self.__class__.__name__

        # Try different name formats:
        # 1. Full class name (e.g., BatteryLevelCharacteristic)
        # 2. Without 'Characteristic' suffix (e.g., BatteryLevel)
        # 3. Space-separated (e.g., Battery Level)
        char_name = name
        if name.endswith("Characteristic"):
            char_name = name[:-14]  # Remove 'Characteristic' suffix

        # Split on camelCase and convert to space-separated
        words = re.findall("[A-Z][^A-Z]*", char_name)
        display_name = " ".join(words)

        names_to_try = [
            name,  # Full class name (e.g. BatteryLevelCharacteristic)
            char_name,  # Without 'Characteristic' suffix
            display_name,  # Space-separated (e.g. Battery Level)
        ]

        # Try each name format with YAML resolution
        for try_name in names_to_try:
            spec = yaml_cross_reference.resolve_characteristic_spec(try_name)
            if spec:
                return spec

        return None

    def _resolve_from_basic_registry(self):
        """Fallback to basic registry resolution (original behavior)."""
        # First try explicit characteristic name if set
        characteristic_name = getattr(self, "_characteristic_name", None)
        if characteristic_name:
            char_info = uuid_registry.get_characteristic_info(characteristic_name)
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

        First tries manual unit override, then YAML cross-reference,
        then falls back to basic YAML registry.
        This allows manual overrides to take precedence while using maximum automation as default.
        """
        # First try manual unit override (takes priority)
        if hasattr(self, "_manual_unit"):
            return self._manual_unit

        # Try unit symbol from cross-file references
        if hasattr(self, "_yaml_unit_symbol") and self._yaml_unit_symbol:
            return self._yaml_unit_symbol

        # Fallback to unit from basic YAML registry
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

    # YAML automation helper methods
    def get_yaml_data_type(self) -> str | None:
        """Get the data type from YAML automation (e.g., 'sint16', 'uint8')."""
        return getattr(self, "_yaml_data_type", None)

    def get_yaml_field_size(self) -> int | None:
        """Get the field size in bytes from YAML automation."""
        field_size = getattr(self, "_yaml_field_size", None)
        if field_size and isinstance(field_size, str) and field_size.isdigit():
            return int(field_size)
        return field_size

    def get_yaml_unit_id(self) -> str | None:
        """Get the Bluetooth SIG unit identifier from YAML automation."""
        return getattr(self, "_yaml_unit_id", None)

    def get_yaml_resolution_text(self) -> str | None:
        """Get the resolution description text from YAML automation."""
        return getattr(self, "_yaml_resolution_text", None)

    def is_signed_from_yaml(self) -> bool:
        """Determine if the data type is signed based on YAML automation."""
        data_type = self.get_yaml_data_type()
        if not data_type:
            return False
        # Check for signed integer types
        if data_type.startswith("sint"):
            return True
        # Check for IEEE-11073 medical float types (signed)
        if data_type in ("medfloat16", "medfloat32"):
            return True
        # Check for IEEE-754 floating point types (signed)
        if data_type in ("float32", "float64"):
            return True
        return False

    def get_byte_order_hint(self) -> str:
        """Get byte order hint (Bluetooth SIG uses little-endian by convention)."""
        return "little"

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
