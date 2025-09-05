"""Base class for GATT characteristics."""

from __future__ import annotations

import re
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..uuid_registry import uuid_registry

# Enhanced YAML automation (try import, fallback to basic registry if not available)
try:
    from ...registry.yaml_cross_reference import yaml_cross_reference
    _enhanced_yaml_available = True
except ImportError:
    _enhanced_yaml_available = False


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
        """Initialize characteristic with UUID from registry based on class name.
        
        Enhanced YAML automation: Automatically resolves metadata from cross-file YAML references
        including UUIDs, data types, field sizes, unit symbols, and byte order hints.
        """
        if not hasattr(self, "_char_uuid"):
            # Enhanced YAML automation - try cross-file resolution first
            if _enhanced_yaml_available:
                enhanced_spec = self._resolve_enhanced_spec()
                if enhanced_spec:
                    self._char_uuid = enhanced_spec.uuid
                    
                    # Enhanced automation: Set additional metadata from YAML
                    if not hasattr(self, "_manual_value_type") and enhanced_spec.data_type:
                        # Map GSS data types to our value types
                        type_mapping = {
                            "sint8": "int", "uint8": "int",
                            "sint16": "int", "uint16": "int", 
                            "sint32": "int", "uint32": "int",
                            "float32": "float", "float64": "float",
                            "utf8s": "string"
                        }
                        self.value_type = type_mapping.get(enhanced_spec.data_type, "bytes")
                        
                    # Store enhanced metadata for manual implementation methods
                    self._enhanced_data_type = enhanced_spec.data_type
                    self._enhanced_field_size = enhanced_spec.field_size
                    self._enhanced_unit_symbol = enhanced_spec.unit_symbol
                    self._enhanced_unit_id = enhanced_spec.unit_id
                    self._enhanced_resolution_text = enhanced_spec.resolution_text
                    
                    return
            
            # Fallback to original registry resolution
            self._resolve_from_basic_registry()
    
    def _resolve_enhanced_spec(self):
        """Resolve specification using enhanced YAML cross-reference system."""
        if not _enhanced_yaml_available:
            return None
            
        # First try explicit characteristic name if set
        if hasattr(self, "_characteristic_name") and self._characteristic_name:
            return yaml_cross_reference.resolve_characteristic_spec(self._characteristic_name)
        
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
        
        # Try each name format with enhanced resolution
        for try_name in names_to_try:
            spec = yaml_cross_reference.resolve_characteristic_spec(try_name)
            if spec:
                return spec
                
        return None
    
    def _resolve_from_basic_registry(self):
        """Fallback to basic registry resolution (original behavior)."""
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

        Enhanced YAML automation: First tries manual unit override, then enhanced YAML 
        cross-reference, then falls back to basic YAML registry.
        This allows manual overrides to take precedence while using maximum automation as default.
        """
        # First try manual unit override (takes priority)
        if hasattr(self, "_manual_unit"):
            return self._manual_unit

        # Enhanced YAML automation: Try enhanced unit symbol from cross-file references
        if hasattr(self, "_enhanced_unit_symbol") and self._enhanced_unit_symbol:
            return self._enhanced_unit_symbol

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

    # Enhanced YAML automation helper methods
    def get_enhanced_data_type(self) -> str | None:
        """Get the data type from enhanced YAML automation (e.g., 'sint16', 'uint8')."""
        return getattr(self, "_enhanced_data_type", None)
    
    def get_enhanced_field_size(self) -> int | None:
        """Get the field size in bytes from enhanced YAML automation."""
        field_size = getattr(self, "_enhanced_field_size", None)
        if field_size and isinstance(field_size, str) and field_size.isdigit():
            return int(field_size)
        return field_size
    
    def get_enhanced_unit_id(self) -> str | None:
        """Get the Bluetooth SIG unit identifier from enhanced YAML automation."""
        return getattr(self, "_enhanced_unit_id", None)
    
    def get_enhanced_resolution_text(self) -> str | None:
        """Get the resolution description text from enhanced YAML automation."""
        return getattr(self, "_enhanced_resolution_text", None)
    
    def is_signed_from_enhanced_yaml(self) -> bool:
        """Determine if the data type is signed based on enhanced YAML automation."""
        data_type = self.get_enhanced_data_type()
        if not data_type:
            return False
        return data_type.startswith("sint")
    
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
