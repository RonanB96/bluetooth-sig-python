"""Base class for GATT characteristics."""

from __future__ import annotations

import re
import struct
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...registry.yaml_cross_reference import CharacteristicSpec, yaml_cross_reference
from ..exceptions import (
    BluetoothSIGError,
    InsufficientDataError,
    TypeMismatchError,
    UUIDResolutionError,
    ValueRangeError,
)
from ..uuid_registry import uuid_registry

if TYPE_CHECKING:
    from ...core import CharacteristicData

_yaml_cross_reference_available = yaml_cross_reference is not None


class CharacteristicMeta(ABCMeta):
    """Metaclass to automatically handle template flags for characteristics."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        # Create the class normally
        new_class = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Auto-handle template flags
        if bases:  # Not the base class itself
            # Check if this class is in templates.py (template) or a concrete implementation
            module_name = namespace.get("__module__", "")
            is_in_templates = "templates" in module_name

            # If it's NOT in templates.py and inherits from a template, mark as concrete
            if not is_in_templates and not namespace.get(
                "_is_template_override", False
            ):
                # Check if any parent has _is_template = True
                has_template_parent = any(
                    getattr(base, "_is_template", False) for base in bases
                )
                if has_template_parent and "_is_template" not in namespace:
                    new_class._is_template = False  # type: ignore[attr-defined] # Mark as concrete characteristic

        return new_class


@dataclass
class BaseCharacteristic(ABC, metaclass=CharacteristicMeta):  # pylint: disable=too-many-instance-attributes
    """Base class for all GATT characteristics.

    Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML specifications.
    Supports manual overrides via _manual_unit and _manual_value_type attributes.

    Validation Attributes (optional class-level declarations):
        min_value: Minimum allowed value for parsed data
        max_value: Maximum allowed value for parsed data
        expected_length: Exact expected data length in bytes
        min_length: Minimum required data length in bytes
        max_length: Maximum allowed data length in bytes
        allow_variable_length: Whether variable length data is acceptable
        expected_type: Expected Python type for parsed values

    Example usage in subclasses:
        @dataclass
        class ExampleCharacteristic(BaseCharacteristic):
            \"\"\"Example showing validation attributes usage.\"\"\"

            # Declare validation constraints as dataclass fields
            expected_length: int = 2
            min_value: int = 0
            max_value: int = 65535
            expected_type: type = int

            def decode_value(self, data: bytearray) -> int:
                # Just parse - validation happens automatically in parse_value
                return DataParser.parse_int16(data, 0, signed=False)

        # Before: BatteryLevelCharacteristic with hardcoded validation
        # @dataclass
        # class BatteryLevelCharacteristic(BaseCharacteristic):
        #     def decode_value(self, data: bytearray) -> int:
        #         if not data:
        #             raise ValueError("Battery level data must be at least 1 byte")
        #         level = data[0]
        #         if not 0 <= level <= 100:
        #             raise ValueError(f"Battery level must be 0-100, got {level}")
        #         return level

        # After: BatteryLevelCharacteristic with declarative validation
        # @dataclass
        # class BatteryLevelCharacteristic(BaseCharacteristic):
        #     expected_length: int = 1
        #     min_value: int = 0
        #     max_value: int = 100
        #     expected_type: type = int
        #
        #     def decode_value(self, data: bytearray) -> int:
        #         return data[0]  # Validation happens automatically
    """

    # Instance variables
    uuid: str
    properties: set[str] = field(default_factory=set)
    value_type: str = field(default="string")

    # Optional validation attributes (can be overridden in subclasses)
    min_value: int | float | None = field(default=None)
    max_value: int | float | None = field(default=None)
    expected_length: int | None = field(default=None)
    min_length: int | None = field(default=None)
    max_length: int | None = field(default=None)
    allow_variable_length: bool = field(default=False)
    expected_type: type | None = field(default=None)

    def __post_init__(self) -> None:
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

    def _resolve_yaml_spec(self) -> CharacteristicSpec | None:
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

    def _resolve_from_basic_registry(self) -> None:
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
            raise UUIDResolutionError(name, names_to_try)

    @property
    def char_uuid(self) -> str:
        """Get the characteristic UUID from registry based on name."""
        return getattr(self, "_char_uuid", "")

    @property
    def name(self) -> str:
        """Get the characteristic name from UUID registry."""
        characteristic_name = getattr(self, "_characteristic_name", None)
        if characteristic_name:
            return str(characteristic_name)
        info = uuid_registry.get_characteristic_info(self.char_uuid)
        return (
            str(info.name)
            if info and info.name
            else f"Unknown Characteristic ({self.char_uuid})"
        )

    @property
    def summary(self) -> str:
        """Get the characteristic summary."""
        info = uuid_registry.get_characteristic_info(self.char_uuid)
        return info.summary if info else ""

    @property
    def display_name(self) -> str:
        """Get the display name for this characteristic.

        Uses explicit _characteristic_name if set, otherwise falls back to class name.
        """
        return getattr(self, "_characteristic_name", self.__class__.__name__)

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
    def decode_value(self, data: bytearray) -> Any:
        """Parse the characteristic's raw value.

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Parsed value in the appropriate type

        Raises:
            NotImplementedError: This is an abstract method
        """
        raise NotImplementedError

    def _validate_range(self, value: Any) -> None:
        """Validate value is within min/max range."""
        if self.min_value is not None and value < self.min_value:
            raise ValueRangeError("value", value, self.min_value, self.max_value)
        if self.max_value is not None and value > self.max_value:
            raise ValueRangeError("value", value, self.min_value, self.max_value)

    def _validate_length(self, data: bytes | bytearray) -> None:
        """Validate data length meets requirements."""
        length = len(data)
        if self.expected_length is not None and length != self.expected_length:
            raise InsufficientDataError(
                "characteristic_data", data, self.expected_length
            )
        if self.min_length is not None and length < self.min_length:
            raise InsufficientDataError("characteristic_data", data, self.min_length)
        if self.max_length is not None and length > self.max_length:
            raise ValueError(f"Maximum {self.max_length} bytes allowed, got {length}")

    def _validate_value(self, value: Any) -> None:
        """Validate parsed value meets all requirements."""
        if self.expected_type is not None and not isinstance(value, self.expected_type):
            raise TypeMismatchError("parsed_value", value, self.expected_type)
        self._validate_range(value)

    def parse_value(self, data: bytes | bytearray) -> CharacteristicData:
        """Parse characteristic data with automatic validation.

        This method automatically validates input data length and parsed values
        based on class-level validation attributes, then returns a CharacteristicData
        object with rich metadata.

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            CharacteristicData object with parsed value and metadata
        """
        # Import here to avoid circular imports
        from ...core import CharacteristicData  # pylint: disable=C0415

        # Call subclass implementation with validation
        try:
            # Validate input data length
            self._validate_length(data)

            parsed_value = self.decode_value(bytearray(data))

            # Validate parsed value
            self._validate_value(parsed_value)

            return CharacteristicData(
                uuid=self.char_uuid,
                name=self.display_name,
                value=parsed_value,
                unit=self.unit,
                value_type=getattr(self, "value_type", None),
                raw_data=bytes(data),
                parse_success=True,
                error_message=None,
            )
        except (ValueError, TypeError, struct.error, BluetoothSIGError) as e:
            return CharacteristicData(
                uuid=self.char_uuid,
                name=self.display_name,
                value=None,
                unit=self.unit,
                value_type=getattr(self, "value_type", None),
                raw_data=bytes(data),
                parse_success=False,
                error_message=str(e),
            )

    @abstractmethod
    def encode_value(self, data: Any) -> bytearray:
        """Encode the characteristic's value to raw bytes.

        Args:
            data: Dataclass instance or value to encode

        Returns:
            Encoded bytes for characteristic write

        Raises:
            ValueError: If data is invalid for encoding
            NotImplementedError: Must be implemented by subclasses
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
        manual_unit = getattr(self, "_manual_unit", None)
        if manual_unit:
            return str(manual_unit)

        # Try unit symbol from cross-file references
        if hasattr(self, "_yaml_unit_symbol") and self._yaml_unit_symbol:
            return self._yaml_unit_symbol

        # Fallback to unit from basic YAML registry
        char_info = uuid_registry.get_characteristic_info(self.char_uuid)
        if char_info and char_info.unit:
            return str(char_info.unit)

        return ""

    @property
    def size(self) -> int | None:
        """Get the size in bytes for this characteristic from YAML specifications.

        Returns the field size from YAML automation if available, otherwise None.
        This is useful for determining the expected data length for parsing and encoding.
        """
        # First try manual size override if set
        if hasattr(self, "_manual_size"):
            manual_size = getattr(self, "_manual_size", None)
            if isinstance(manual_size, int):
                return manual_size

        # Try field size from YAML cross-reference
        field_size = self.get_yaml_field_size()
        if field_size is not None:
            return field_size

        # For characteristics without YAML size info, return None
        # indicating variable or unknown length
        return None

    @property
    def value_type_resolved(self) -> str:
        """Get the value type for this characteristic.

        First tries manual value_type override, then falls back to YAML registry.
        This allows manual overrides to take precedence while using automatic parsing as default.
        """
        # First try manual value_type override (takes priority)
        manual_value_type = getattr(self, "_manual_value_type", None)
        if manual_value_type:
            return str(manual_value_type)

        # Fallback to value_type from YAML registry for automatic parsing
        char_info = uuid_registry.get_characteristic_info(self.char_uuid)
        if char_info and char_info.value_type:
            return str(char_info.value_type)

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
        if isinstance(field_size, int):
            return field_size
        return None

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

    @classmethod
    def from_uuid(
        cls, uuid: str, properties: set[str] | None = None
    ) -> BaseCharacteristic:
        """Create a characteristic instance from UUID.

        Args:
            uuid: Characteristic UUID
            properties: Set of GATT properties (optional)

        Returns:
            Characteristic instance
        """
        if properties is None:
            properties = set()
        return cls(uuid=uuid, properties=properties)
