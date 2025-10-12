"""Base class for GATT characteristics."""
# pylint: disable=too-many-lines

from __future__ import annotations

import os
import re
import struct
from abc import ABC, ABCMeta
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from bluetooth_sig.gatt.characteristics.templates import CodingTemplate

from ...registry.yaml_cross_reference import CharacteristicSpec, yaml_cross_reference
from ...types import CharacteristicData, CharacteristicInfo
from ...types.data_types import ParseFieldError
from ...types.gatt_enums import CharacteristicName, GattProperty, ValueType
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..exceptions import (
    BluetoothSIGError,
    InsufficientDataError,
    TypeMismatchError,
    UUIDResolutionError,
    ValueRangeError,
)
from ..exceptions import (
    ParseFieldError as ParseFieldException,
)
from ..resolver import CharacteristicRegistrySearch, NameNormalizer, NameVariantGenerator
from ..uuid_registry import uuid_registry
from .utils.parse_trace import ParseTrace


@dataclass
class ValidationConfig:
    """Configuration for characteristic validation constraints.

    Groups validation parameters into a single, optional configuration object
    to simplify BaseCharacteristic constructor signatures.
    """

    min_value: int | float | None = None
    max_value: int | float | None = None
    expected_length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    allow_variable_length: bool = False
    expected_type: type | None = None


class SIGCharacteristicResolver:
    """Resolves SIG characteristic information from YAML and registry.

    This class handles all SIG characteristic resolution logic, separating
    concerns from the BaseCharacteristic constructor. Uses shared utilities
    from the resolver module to avoid code duplication.
    """

    camel_case_to_display_name = staticmethod(NameNormalizer.camel_case_to_display_name)

    @staticmethod
    def resolve_for_class(char_class: type[BaseCharacteristic]) -> CharacteristicInfo:
        """Resolve CharacteristicInfo for a SIG characteristic class.

        Args:
            char_class: The characteristic class to resolve info for

        Returns:
            CharacteristicInfo with resolved UUID, name, value_type, unit

        Raises:
            UUIDResolutionError: If no UUID can be resolved for the class
        """
        # Try YAML resolution first
        yaml_spec = SIGCharacteristicResolver.resolve_yaml_spec_for_class(char_class)
        if yaml_spec:
            return SIGCharacteristicResolver._create_info_from_yaml(yaml_spec, char_class)

        # Fallback to registry
        registry_info = SIGCharacteristicResolver.resolve_from_registry(char_class)
        if registry_info:
            return registry_info

        # No resolution found
        raise UUIDResolutionError(char_class.__name__, [char_class.__name__])

    @staticmethod
    def resolve_yaml_spec_for_class(char_class: type[BaseCharacteristic]) -> CharacteristicSpec | None:
        """Resolve YAML spec for a characteristic class using shared name variant logic."""
        # Get explicit name if set
        characteristic_name = getattr(char_class, "_characteristic_name", None)

        # Generate all name variants using shared utility
        names_to_try = NameVariantGenerator.generate_characteristic_variants(char_class.__name__, characteristic_name)

        # Try each name format with YAML resolution
        for try_name in names_to_try:
            spec = yaml_cross_reference.resolve_characteristic_spec(try_name)
            if spec:
                return spec

        return None

    @staticmethod
    def _create_info_from_yaml(
        yaml_spec: CharacteristicSpec, char_class: type[BaseCharacteristic]
    ) -> CharacteristicInfo:
        """Create CharacteristicInfo from YAML spec."""
        # Map GSS data types to our value types
        type_mapping = {
            "sint8": ValueType.INT,
            "uint8": ValueType.INT,
            "sint16": ValueType.INT,
            "uint16": ValueType.INT,
            "uint24": ValueType.INT,
            "sint32": ValueType.INT,
            "uint32": ValueType.INT,
            "float32": ValueType.FLOAT,
            "float64": ValueType.FLOAT,
            "sfloat": ValueType.FLOAT,  # IEEE-11073 16-bit SFLOAT
            "float": ValueType.FLOAT,  # IEEE-11073 32-bit FLOAT
            "medfloat16": ValueType.FLOAT,  # Medical float 16-bit
            "utf8s": ValueType.STRING,
            "utf16s": ValueType.STRING,
            "boolean": ValueType.BOOL,
            "struct": ValueType.BYTES,
            "variable": ValueType.BYTES,
        }

        value_type = (
            type_mapping.get(yaml_spec.data_type, ValueType.UNKNOWN) if yaml_spec.data_type else ValueType.UNKNOWN
        )

        return CharacteristicInfo(
            uuid=yaml_spec.uuid,
            name=yaml_spec.name or char_class.__name__,
            unit=yaml_spec.unit_symbol or "",
            value_type=value_type,
            properties=[],  # Properties will be resolved separately if needed
        )

    @staticmethod
    def resolve_from_registry(char_class: type[BaseCharacteristic]) -> CharacteristicInfo | None:
        """Fallback to registry resolution using shared search strategy."""
        # Use shared registry search strategy
        search_strategy = CharacteristicRegistrySearch()
        characteristic_name = getattr(char_class, "_characteristic_name", None)
        return search_strategy.search(char_class, characteristic_name)


class CharacteristicMeta(ABCMeta):
    """Metaclass to automatically handle template flags for characteristics."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        # Auto-handle template flags before class creation so attributes are part of namespace
        if bases:  # Not the base class itself
            # Check if this class is in templates.py (template) or a concrete implementation
            module_name = namespace.get("__module__", "")
            is_in_templates = "templates" in module_name

            # If it's NOT in templates.py and inherits from a template, mark as concrete
            if not is_in_templates and not namespace.get("_is_template_override", False):
                # Check if any parent has _is_template = True
                has_template_parent = any(getattr(base, "_is_template", False) for base in bases)
                if has_template_parent and "_is_template" not in namespace:
                    namespace["_is_template"] = False  # Mark as concrete characteristic

        # Create the class normally
        new_class = super().__new__(mcs, name, bases, namespace, **kwargs)

        return new_class


class BaseCharacteristic(ABC, metaclass=CharacteristicMeta):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Base class for all GATT characteristics.

    Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML specifications.
    Supports manual overrides via _manual_unit and _manual_value_type attributes.

    Note: This class intentionally has >20 public methods as it provides the complete
    characteristic API including parsing, validation, UUID resolution, registry interaction,
    and metadata access. The methods are well-organized by functionality.

    Validation Attributes (optional class-level declarations):
        min_value: Minimum allowed value for parsed data
        max_value: Maximum allowed value for parsed data
        expected_length: Exact expected data length in bytes
        min_length: Minimum required data length in bytes
        max_length: Maximum allowed data length in bytes
        allow_variable_length: Whether variable length data is acceptable
        expected_type: Expected Python type for parsed values

    Example usage in subclasses:
        class ExampleCharacteristic(BaseCharacteristic):
            \"\"\"Example showing validation attributes usage.\"\"\"

            # Declare validation constraints as class attributes
            expected_length = 2
            min_value = 0
            max_value = 65535  # UINT16_MAX
            expected_type = int

            def decode_value(self, data: bytearray) -> int:
                # Just parse - validation happens automatically in parse_value
                return DataParser.parse_int16(data, 0, signed=False)

        # Before: BatteryLevelCharacteristic with hardcoded validation
        # class BatteryLevelCharacteristic(BaseCharacteristic):
        #     def decode_value(self, data: bytearray) -> int:
        #         if not data:
        #             raise ValueError("Battery level data must be at least 1 byte")
        #         level = data[0]
        #         if not 0 <= level <= PERCENTAGE_MAX:
        #             raise ValueError(f"Battery level must be 0-100, got {level}")
        #         return level

        # After: BatteryLevelCharacteristic with declarative validation
        # class BatteryLevelCharacteristic(BaseCharacteristic):
        #     expected_length = 1
        #     min_value = 0
        #     max_value = 100  # PERCENTAGE_MAX
        #     expected_type = int
        #
        #     def decode_value(self, data: bytearray) -> int:
        #         return data[0]  # Validation happens automatically
    """

    # Explicit class attributes with defaults (replaces getattr usage)
    _characteristic_name: str | None = None
    _manual_unit: str | None = None
    _manual_value_type: ValueType | str | None = None
    _manual_size: int | None = None
    _is_template: bool = False

    # Validation attributes (Progressive API Level 2)
    min_value: int | float | None = None
    max_value: int | float | None = None
    expected_length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    allow_variable_length: bool = False
    expected_type: type | None = None

    # Template support (Progressive API Level 4)
    _template: CodingTemplate | None = None  # CodingTemplate instance for composition

    # YAML automation attributes
    _yaml_data_type: str | None = None
    _yaml_field_size: int | str | None = None
    _yaml_unit_id: str | None = None
    _yaml_resolution_text: str | None = None

    _allows_sig_override = False

    # Multi-characteristic parsing support (Progressive API Level 5)
    _required_dependencies: list[type[BaseCharacteristic]] = []  # Dependencies that MUST be present
    _optional_dependencies: list[type[BaseCharacteristic]] = []  # Dependencies that enrich parsing when available

    # Parse trace control (for performance tuning)
    # Can be configured via BLUETOOTH_SIG_ENABLE_PARSE_TRACE environment variable
    # Set to "0", "false", or "no" to disable trace collection
    _enable_parse_trace: bool = True  # Default: enabled

    def __init__(
        self,
        info: CharacteristicInfo | None = None,
        validation: ValidationConfig | None = None,
    ) -> None:
        """Initialize characteristic with structured configuration.

        Args:
            info: Complete characteristic information (optional for SIG characteristics)
            validation: Validation constraints configuration (optional)
        """
        # Store provided info or None (will be resolved in __post_init__)
        self._provided_info = info

        # Instance variables (will be set in __post_init__)
        self._info: CharacteristicInfo

        # Manual overrides with proper types (using explicit class attributes)
        self._manual_unit: str | None = self.__class__._manual_unit
        self._manual_value_type: ValueType | str | None = self.__class__._manual_value_type
        self.value_type: ValueType = ValueType.UNKNOWN

        # Set validation attributes from ValidationConfig or class defaults
        if validation:
            self.min_value = validation.min_value
            self.max_value = validation.max_value
            self.expected_length = validation.expected_length
            self.min_length = validation.min_length
            self.max_length = validation.max_length
            self.allow_variable_length = validation.allow_variable_length
            self.expected_type = validation.expected_type
        else:
            # Fall back to class attributes for Progressive API Level 2
            self.min_value = self.__class__.min_value
            self.max_value = self.__class__.max_value
            self.expected_length = self.__class__.expected_length
            self.min_length = self.__class__.min_length
            self.max_length = self.__class__.max_length
            self.allow_variable_length = self.__class__.allow_variable_length
            self.expected_type = self.__class__.expected_type

        # Dependency caches (resolved once per instance)
        self._resolved_required_dependencies: list[str] | None = None
        self._resolved_optional_dependencies: list[str] | None = None

        # Call post-init to resolve characteristic info
        self.__post_init__()

    def __post_init__(self) -> None:
        """Initialize characteristic with resolved information."""
        # Use provided info if available, otherwise resolve from SIG specs
        if self._provided_info:
            self._info = self._provided_info
        else:
            # Resolve characteristic information using proper resolver
            self._info = SIGCharacteristicResolver.resolve_for_class(type(self))
        # Apply manual overrides to _info (single source of truth)
        if self._manual_unit is not None:
            self._info.unit = self._manual_unit
        if self._manual_value_type is not None:
            # Handle both ValueType enum and string manual overrides
            if isinstance(self._manual_value_type, ValueType):
                self._info.value_type = self._manual_value_type
            else:
                # Map string value types to ValueType enum
                string_to_value_type_map = {
                    "string": ValueType.STRING,
                    "int": ValueType.INT,
                    "float": ValueType.FLOAT,
                    "bytes": ValueType.BYTES,
                    "bool": ValueType.BOOL,
                    "datetime": ValueType.DATETIME,
                    "uuid": ValueType.UUID,
                    "dict": ValueType.DICT,
                    "various": ValueType.VARIOUS,
                    "unknown": ValueType.UNKNOWN,
                    # Custom type strings that should map to basic types
                    "BarometricPressureTrend": ValueType.INT,  # IntEnum -> int
                }

                try:
                    # First try direct ValueType enum construction
                    self._info.value_type = ValueType(self._manual_value_type)
                except ValueError:
                    # Fall back to string mapping
                    self._info.value_type = string_to_value_type_map.get(self._manual_value_type, ValueType.VARIOUS)

        # Set value_type from resolved info
        self.value_type = self._info.value_type

        # If value_type is still UNKNOWN after resolution and no manual override,
        # try to infer from characteristic patterns
        if self.value_type == ValueType.UNKNOWN and self._manual_value_type is None:
            inferred_type = self._infer_value_type_from_patterns()
            if inferred_type != ValueType.UNKNOWN:
                self._info.value_type = inferred_type
                self.value_type = inferred_type

    def _infer_value_type_from_patterns(self) -> ValueType:
        """Infer value type from characteristic naming patterns and class structure.

        This provides a fallback when SIG resolution fails to determine proper value types.
        """
        class_name = self.__class__.__name__
        char_name = self._characteristic_name or class_name

        # Pattern-based inference for common characteristics
        measurement_patterns = [
            "Measurement",
            "Data",
            "Reading",
            "Value",
            "Status",
            "Feature",
            "Capability",
            "Support",
            "Configuration",
        ]

        # If it contains measurement/data patterns, likely returns complex data -> bytes
        if any(pattern in class_name or pattern in char_name for pattern in measurement_patterns):
            return ValueType.BYTES

        # Common simple value characteristics
        simple_int_patterns = ["Level", "Count", "Index", "ID", "Appearance"]
        if any(pattern in class_name or pattern in char_name for pattern in simple_int_patterns):
            return ValueType.INT

        simple_string_patterns = ["Name", "Description", "Text", "String"]
        if any(pattern in class_name or pattern in char_name for pattern in simple_string_patterns):
            return ValueType.STRING

        # Default fallback for complex characteristics
        return ValueType.BYTES

    def _resolve_yaml_spec(self) -> CharacteristicSpec | None:
        """Resolve specification using YAML cross-reference system."""
        # Delegate to static method
        return SIGCharacteristicResolver.resolve_yaml_spec_for_class(type(self))

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the characteristic UUID from _info (single source of truth)."""
        return self._info.uuid

    @property
    def info(self) -> CharacteristicInfo:
        """Get the characteristic info (single source of truth)."""
        return self._info

    @property
    def name(self) -> str:
        """Get the characteristic name from _info (single source of truth)."""
        return self._info.name

    @property
    def summary(self) -> str:
        """Get the characteristic summary."""
        # NOTE: For single source of truth, we should use _info but CharacteristicInfo
        # doesn't currently include summary field. This is a temporary compromise
        # until CharacteristicInfo is enhanced with summary field
        info = uuid_registry.get_characteristic_info(self._info.uuid)
        return info.summary if info else ""

    @property
    def display_name(self) -> str:
        """Get the display name for this characteristic.

        Uses explicit _characteristic_name if set, otherwise falls back
        to class name.
        """
        return self._characteristic_name or self.__class__.__name__

    @classmethod
    def _normalize_dependency_class(cls, dep_class: type[BaseCharacteristic]) -> str | None:
        """Resolve a dependency class to its canonical UUID string.

        Args:
            dep_class: The characteristic class to resolve

        Returns:
            Canonical UUID string or None if unresolvable
        """
        configured_info: CharacteristicInfo | None = getattr(dep_class, "_info", None)
        if configured_info is not None:
            return str(configured_info.uuid)

        try:
            class_uuid = dep_class.get_class_uuid()
            if class_uuid is not None:
                return str(class_uuid)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        try:
            temp_instance = dep_class()
            return str(temp_instance.info.uuid)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def _resolve_dependencies(self, attr_name: str) -> list[str]:
        """Resolve dependency class references to canonical UUID strings."""

        dependency_classes: list[type[BaseCharacteristic]] = []

        declared = getattr(self.__class__, attr_name, []) or []
        dependency_classes.extend(declared)

        resolved: list[str] = []
        seen: set[str] = set()

        for dep_class in dependency_classes:
            uuid_str = self._normalize_dependency_class(dep_class)
            if uuid_str and uuid_str not in seen:
                seen.add(uuid_str)
                resolved.append(uuid_str)

        return resolved

    @property
    def required_dependencies(self) -> list[str]:
        """Get resolved required dependency UUID strings."""

        if self._resolved_required_dependencies is None:
            self._resolved_required_dependencies = self._resolve_dependencies("_required_dependencies")

        return list(self._resolved_required_dependencies)

    @property
    def optional_dependencies(self) -> list[str]:
        """Get resolved optional dependency UUID strings."""

        if self._resolved_optional_dependencies is None:
            self._resolved_optional_dependencies = self._resolve_dependencies("_optional_dependencies")

        return list(self._resolved_optional_dependencies)

    @classmethod
    def get_allows_sig_override(cls) -> bool:
        """Check if this characteristic class allows overriding SIG characteristics.

        Custom characteristics that need to override official Bluetooth SIG
        characteristics must set _allows_sig_override = True as a class attribute.

        Returns:
            True if SIG override is allowed, False otherwise.
        """
        return cls._allows_sig_override

    @classmethod
    def get_class_uuid(cls) -> BluetoothUUID | None:
        """Get the characteristic UUID for this class without creating an instance.

        This is the public API for registry and other modules to resolve UUIDs.

        Returns:
            BluetoothUUID if the class has a resolvable UUID, None otherwise.
        """
        return cls._resolve_class_uuid()

    @classmethod
    def _resolve_class_uuid(cls) -> BluetoothUUID | None:
        """Resolve the characteristic UUID for this class without creating an instance."""
        # Try cross-file resolution first
        yaml_spec = cls._resolve_yaml_spec_class()
        if yaml_spec:
            return yaml_spec.uuid

        # Fallback to original registry resolution
        return cls._resolve_from_basic_registry_class()

    @classmethod
    def _resolve_yaml_spec_class(cls) -> CharacteristicSpec | None:
        """Resolve specification using YAML cross-reference system at class level."""
        return SIGCharacteristicResolver.resolve_yaml_spec_for_class(cls)

    @classmethod
    def _resolve_from_basic_registry_class(cls) -> BluetoothUUID | None:
        """Fallback to basic registry resolution at class level."""
        try:
            registry_info = SIGCharacteristicResolver.resolve_from_registry(cls)
            return registry_info.uuid if registry_info else None
        except (ValueError, KeyError, AttributeError, TypeError):
            # Registry resolution can fail for various reasons:
            # - ValueError: Invalid UUID format
            # - KeyError: Characteristic not in registry
            # - AttributeError: Missing expected attributes
            # - TypeError: Type mismatch in resolution
            return None

    @classmethod
    def matches_uuid(cls, uuid: str | BluetoothUUID) -> bool:
        """Check if this characteristic matches the given UUID."""
        try:
            class_uuid = cls._resolve_class_uuid()
            if class_uuid is None:
                return False
            if isinstance(uuid, BluetoothUUID):
                input_uuid = uuid
            else:
                input_uuid = BluetoothUUID(uuid)
            return class_uuid == input_uuid
        except ValueError:
            return False

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> Any:
        """Parse the characteristic's raw value.

        If _template is set (Level 4 Progressive API), uses the template's decode_value method.
        Otherwise, subclasses must override this method.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context information for parsing

        Returns:
            Parsed value in the appropriate type

        Raises:
            NotImplementedError: If no template is set and subclass doesn't override
        """
        if self._template is not None:
            return self._template.decode_value(data, offset=0, ctx=ctx)
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override decode_value()")

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
            raise InsufficientDataError("characteristic_data", data, self.expected_length)
        if self.min_length is not None and length < self.min_length:
            raise InsufficientDataError("characteristic_data", data, self.min_length)
        if self.max_length is not None and length > self.max_length:
            raise ValueError(f"Maximum {self.max_length} bytes allowed, got {length}")

    def _validate_value(self, value: Any) -> None:
        """Validate parsed value meets all requirements."""
        if self.expected_type is not None and not isinstance(value, self.expected_type):
            raise TypeMismatchError("parsed_value", value, self.expected_type)
        self._validate_range(value)

    @staticmethod
    @lru_cache(maxsize=32)
    def _get_characteristic_uuid_by_name(
        characteristic_name: CharacteristicName | CharacteristicName | str,
    ) -> str | None:
        """Get characteristic UUID by name using cached registry lookup."""
        # Convert enum to string value for registry lookup
        name_str = (
            characteristic_name.value if isinstance(characteristic_name, CharacteristicName) else characteristic_name
        )
        char_info = uuid_registry.get_characteristic_info(name_str)
        return str(char_info.uuid) if char_info else None

    def get_context_characteristic(
        self,
        ctx: CharacteristicContext | None,
        characteristic_name: CharacteristicName | str | type[BaseCharacteristic],
    ) -> Any | None:
        """Generic utility to find a characteristic in context by name or class.

        Args:
            ctx: Context containing other characteristics
            characteristic_name: Enum, string name, or characteristic class

        Returns:
            Characteristic data if found, None otherwise
        """
        if not ctx or not ctx.other_characteristics:
            return None

        # Extract UUID from class if provided
        if isinstance(characteristic_name, type):
            # Class reference provided - try to get class-level UUID
            configured_info: CharacteristicInfo | None = getattr(characteristic_name, "_configured_info", None)
            if configured_info is not None:
                # Custom characteristic with explicit _configured_info
                char_uuid: str = str(configured_info.uuid)
            else:
                # SIG characteristic: convert class name to SIG name and resolve via registry
                class_name: str = characteristic_name.__name__
                # Remove 'Characteristic' suffix
                name_without_suffix: str = class_name.replace("Characteristic", "")
                # Insert spaces before capital letters to get SIG name
                sig_name: str = re.sub(r"(?<!^)(?=[A-Z])", " ", name_without_suffix)
                # Look up UUID via registry
                resolved_uuid: str | None = self._get_characteristic_uuid_by_name(sig_name)
                if resolved_uuid is None:
                    return None
                char_uuid = resolved_uuid
        else:
            # Enum or string name
            resolved_uuid = self._get_characteristic_uuid_by_name(characteristic_name)
            if resolved_uuid is None:
                return None
            char_uuid = resolved_uuid

        return ctx.other_characteristics.get(char_uuid)

    @staticmethod
    def _is_parse_trace_enabled() -> bool:
        """Check if parse trace is enabled via environment variable or class default.

        Returns:
            True if parse tracing is enabled, False otherwise

        Environment Variables:
            BLUETOOTH_SIG_ENABLE_PARSE_TRACE: Set to "0", "false", or "no" to disable
        """
        env_value = os.getenv("BLUETOOTH_SIG_ENABLE_PARSE_TRACE", "").lower()
        if env_value in ("0", "false", "no"):
            return False
        # Default to class attribute if env var not set
        return True

    def parse_value(self, data: bytes | bytearray, ctx: Any | None = None) -> CharacteristicData:
        """Parse characteristic data with automatic validation.

        This method automatically validates input data length and parsed values
        based on class-level validation attributes, then returns a CharacteristicData
        object with rich metadata including field-level errors and parse traces.

        Parse trace collection can be disabled by:
        1. Setting BLUETOOTH_SIG_ENABLE_PARSE_TRACE environment variable to "0", "false", or "no"
        2. Setting _enable_parse_trace = False on the characteristic class

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context information for parsing

        Returns:
            CharacteristicData object with parsed value, metadata, field errors, and parse trace
        """
        # Check both environment variable and class attribute
        trace_enabled = self._is_parse_trace_enabled() and self._enable_parse_trace

        # Initialize trace and field error collection using ParseTrace class
        trace = ParseTrace(enabled=trace_enabled)
        field_errors: list[ParseFieldError] = []

        # Call subclass implementation with validation
        try:
            trace.append(f"Starting parse of {self._info.name}")

            # Validate input data length
            trace.append(f"Validating data length (got {len(data)} bytes)")
            self._validate_length(data)

            trace.append("Decoding value")
            parsed_value = self.decode_value(bytearray(data), ctx)

            # Validate parsed value
            trace.append(f"Validating parsed value (type: {type(parsed_value).__name__})")
            self._validate_value(parsed_value)

            trace.append("Parse completed successfully")

            return CharacteristicData(
                info=self._info,  # Use _info as single source of truth
                value=parsed_value,
                raw_data=bytes(data),
                parse_success=True,
                error_message="",
                field_errors=[],
                parse_trace=trace.get_trace(),
            )
        except (ValueError, TypeError, struct.error, BluetoothSIGError) as e:
            # Extract field information from ParseFieldException if available
            if isinstance(e, ParseFieldException):
                field_errors.append(
                    ParseFieldError(
                        field=e.field,
                        reason=e.field_reason,  # Use field_reason which stores the original reason
                        offset=e.offset,
                        raw_slice=bytes(data),
                    )
                )
                trace.append(f"Field error in '{e.field}': {e.field_reason}")
            else:
                # Generic error - report without trying to extract field details
                trace.append(f"Parse failed: {str(e)}")

            return CharacteristicData(
                info=self._info,  # Use _info as single source of truth
                value=None,
                raw_data=bytes(data),
                parse_success=False,
                error_message=str(e),
                field_errors=field_errors,
                parse_trace=trace.get_trace(),
            )

    def encode_value(self, data: Any) -> bytearray:
        """Encode the characteristic's value to raw bytes.

        If _template is set (Level 4 Progressive API), uses the template's encode_value method.
        Otherwise, subclasses must override this method.

        Args:
            data: Dataclass instance or value to encode

        Returns:
            Encoded bytes for characteristic write

        Raises:
            ValueError: If data is invalid for encoding
            NotImplementedError: If no template is set and subclass doesn't override
        """
        if self._template is not None:
            return self._template.encode_value(data)
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override encode_value()")

    @property
    def unit(self) -> str:
        """Get the unit of measurement from _info (single source of truth)."""
        return self._info.unit

    @property
    def properties(self) -> list[GattProperty]:
        """Get the GATT properties from _info (single source of truth)."""
        return self._info.properties

    @property
    def size(self) -> int | None:
        """Get the size in bytes for this characteristic from YAML
        specifications.

        Returns the field size from YAML automation if available,
        otherwise None. This is useful for determining the expected data
        length for parsing and encoding.
        """
        # First try manual size override if set
        if self._manual_size is not None:
            return self._manual_size

        # Try field size from YAML cross-reference
        field_size = self.get_yaml_field_size()
        if field_size is not None:
            return field_size

        # For characteristics without YAML size info, return None
        # indicating variable or unknown length
        return None

    @property
    def value_type_resolved(self) -> ValueType:
        """Get the value type from _info (single source of truth)."""
        return self._info.value_type

    # YAML automation helper methods
    def get_yaml_data_type(self) -> str | None:
        """Get the data type from YAML automation (e.g., 'sint16', 'uint8')."""
        return self._yaml_data_type

    def get_yaml_field_size(self) -> int | None:
        """Get the field size in bytes from YAML automation."""
        field_size = self._yaml_field_size
        if field_size and isinstance(field_size, str) and field_size.isdigit():
            return int(field_size)
        if isinstance(field_size, int):
            return field_size
        return None

    def get_yaml_unit_id(self) -> str | None:
        """Get the Bluetooth SIG unit identifier from YAML automation."""
        return self._yaml_unit_id

    def get_yaml_resolution_text(self) -> str | None:
        """Get the resolution description text from YAML automation."""
        return self._yaml_resolution_text

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
        """Get byte order hint (Bluetooth SIG uses little-endian by
        convention)."""
        return "little"


class CustomBaseCharacteristic(BaseCharacteristic):
    """Helper base class for custom characteristic implementations.

    This class provides a wrapper around physical BLE characteristics that are not
    defined in the Bluetooth SIG specification. It supports both manual info passing
    and automatic class-level _info binding via __init_subclass__.

    Progressive API Levels Supported:
    - Level 2: Class-level _info attribute (automatic binding)
    - Legacy: Manual info parameter (backwards compatibility)
    """

    _is_custom = True
    _configured_info: CharacteristicInfo | None = None  # Stores class-level _info
    _allows_sig_override = False  # Default: no SIG override permission

    # pylint: disable=duplicate-code
    # NOTE: __init_subclass__ and __init__ patterns are intentionally similar to CustomBaseService.
    # This is by design - both custom characteristic and service classes need identical validation
    # and info management patterns. Consolidation not possible due to different base types and info types.
    def __init_subclass__(cls, allow_sig_override: bool = False, **kwargs: Any) -> None:
        """Automatically set up _info if provided as class attribute.

        Args:
            allow_sig_override: Set to True when intentionally overriding SIG UUIDs

        Raises:
            ValueError: If class uses SIG UUID without override permission
        """
        super().__init_subclass__(**kwargs)

        # Store override permission for registry validation
        cls._allows_sig_override = allow_sig_override

        # If class has _info attribute, validate and store it
        if hasattr(cls, "_info"):
            info = getattr(cls, "_info", None)
            if info is not None:
                # Check for SIG UUID override (unless explicitly allowed)
                if not allow_sig_override and info.uuid.is_sig_characteristic():
                    raise ValueError(
                        f"{cls.__name__} uses SIG UUID {info.uuid} without override flag. "
                        "Use custom UUID or add allow_sig_override=True parameter."
                    )

                cls._configured_info = info

    def __init__(
        self,
        info: CharacteristicInfo | None = None,
    ) -> None:
        """Initialize a custom characteristic with automatic _info resolution.

        Args:
            info: Optional override for class-configured _info

        Raises:
            ValueError: If no valid info available from class or parameter
        """
        # Use provided info, or fall back to class-configured _info
        final_info = info or self.__class__._configured_info

        if not final_info:
            raise ValueError(f"{self.__class__.__name__} requires either 'info' parameter or '_info' class attribute")

        if not final_info.uuid or str(final_info.uuid) == "0000":
            raise ValueError("Valid UUID is required for custom characteristics")

        # Call parent constructor with our info to maintain consistency
        super().__init__(info=final_info)

    def __post_init__(self) -> None:
        """Override BaseCharacteristic.__post_init__ to use custom info management.

        CustomBaseCharacteristic manages _info manually from provided or configured info,
        bypassing SIG resolution that would fail for custom characteristics.
        """
        # Use provided info if available (from manual override), otherwise use configured info
        if hasattr(self, "_provided_info") and self._provided_info:
            self._info = self._provided_info
        elif self.__class__._configured_info:  # pylint: disable=protected-access
            # Access to _configured_info is intentional for class-level info management
            self._info = self.__class__._configured_info  # pylint: disable=protected-access
        else:
            # This shouldn't happen if class setup is correct
            raise ValueError(f"CustomBaseCharacteristic {self.__class__.__name__} has no valid info source")


class UnknownCharacteristic(CustomBaseCharacteristic):
    """Generic characteristic implementation for unknown/non-SIG characteristics.

    This class provides basic functionality for characteristics that are not
    defined in the Bluetooth SIG specification. It stores raw data without
    attempting to parse it into structured types.
    """

    def __init__(self, info: CharacteristicInfo) -> None:
        """Initialize an unknown characteristic.

        Args:
            info: CharacteristicInfo object with UUID, name, unit, value_type, properties

        Raises:
            ValueError: If UUID is invalid
        """
        # If no name provided, generate one from UUID
        if not info.name:
            info = CharacteristicInfo(
                uuid=info.uuid,
                name=f"Unknown Characteristic ({info.uuid})",
                unit=info.unit or "",
                value_type=info.value_type or ValueType.BYTES,
                properties=info.properties or [],
            )

        super().__init__(info=info)

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> bytes:
        """Return raw bytes for unknown characteristics.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context (ignored)

        Returns:
            Raw bytes as-is
        """
        return bytes(data)

    def encode_value(self, data: Any) -> bytearray:
        """Encode data to bytes for unknown characteristics.

        Args:
            data: Data to encode (must be bytes or bytearray)

        Returns:
            Encoded bytes

        Raises:
            ValueError: If data is not bytes/bytearray
        """
        if isinstance(data, (bytes, bytearray)):
            return bytearray(data)
        raise ValueError(f"Unknown characteristics require bytes data, got {type(data)}")
