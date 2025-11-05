"""Base class for GATT characteristics."""
# pylint: disable=too-many-lines

from __future__ import annotations

import os
import re
from abc import ABC, ABCMeta
from functools import lru_cache
from typing import Any

import msgspec

from ...registry import units_registry
from ...types import CharacteristicData, CharacteristicDataProtocol, CharacteristicInfo, DescriptorData
from ...types import ParseFieldError as FieldError
from ...types.gatt_enums import CharacteristicName, DataType, GattProperty, ValueType
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..descriptors import BaseDescriptor
from ..descriptors.cccd import CCCDDescriptor
from ..descriptors.characteristic_presentation_format import (
    CharacteristicPresentationFormatData,
    CharacteristicPresentationFormatDescriptor,
)
from ..descriptors.characteristic_user_description import (
    CharacteristicUserDescriptionDescriptor,
)
from ..descriptors.valid_range import ValidRangeDescriptor
from ..exceptions import (
    InsufficientDataError,
    ParseFieldError,
    UUIDResolutionError,
    ValueRangeError,
)
from ..resolver import CharacteristicRegistrySearch, NameNormalizer, NameVariantGenerator
from ..uuid_registry import CharacteristicSpec, uuid_registry
from .templates import CodingTemplate


class ValidationConfig(msgspec.Struct, kw_only=True):
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
            spec = uuid_registry.resolve_characteristic_spec(try_name)
            if spec:
                return spec

        return None

    @staticmethod
    def _create_info_from_yaml(
        yaml_spec: CharacteristicSpec, char_class: type[BaseCharacteristic]
    ) -> CharacteristicInfo:
        """Create CharacteristicInfo from YAML spec, resolving metadata via registry classes."""
        value_type = DataType.from_string(yaml_spec.data_type).to_value_type()

        # Resolve unit via registry if present
        unit_info = None
        unit_name = getattr(yaml_spec, "unit_symbol", None) or getattr(yaml_spec, "unit", None)
        if unit_name:
            unit_info = units_registry.get_unit_info_by_name(unit_name)
        if unit_info:
            # Prefer symbol, fallback to name, always ensure string
            unit_symbol = str(getattr(unit_info, "symbol", getattr(unit_info, "name", unit_name)))
        else:
            unit_symbol = str(unit_name or "")

        # TODO: Add similar logic for object types, service classes, etc. as needed

        return CharacteristicInfo(
            uuid=yaml_spec.uuid,
            name=yaml_spec.name or char_class.__name__,
            unit=unit_symbol,
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
        **kwargs: Any,  # noqa: ANN401  # Metaclass receives arbitrary keyword arguments
    ) -> type:
        """Create the characteristic class and handle template markers.

        This metaclass hook ensures template classes and concrete
        implementations are correctly annotated with the ``_is_template``
        attribute before the class object is created.
        """
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
            '''Example showing validation attributes usage.'''

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

        # Descriptor support
        self._descriptors: dict[str, BaseDescriptor] = {}

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
        """Get the characteristic UUID from _info."""
        return self._info.uuid

    @property
    def info(self) -> CharacteristicInfo:
        """Characteristic information."""
        return self._info

    @property
    def name(self) -> str:
        """Get the characteristic name from _info."""
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
        except (ValueError, AttributeError, TypeError):
            pass

        try:
            temp_instance = dep_class()
            return str(temp_instance.info.uuid)
        except (ValueError, AttributeError, TypeError):
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
    def get_configured_info(cls) -> CharacteristicInfo | None:
        """Get the class-level configured CharacteristicInfo.

        This provides public access to the _configured_info attribute that is set
        by __init_subclass__ for custom characteristics.

        Returns:
            CharacteristicInfo if configured, None otherwise

        """
        return getattr(cls, "_configured_info", None)

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

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> Any:  # noqa: ANN401  # Context and return types vary by characteristic
        """Parse the characteristic's raw value.

        If _template is set, uses the template's decode_value method.
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

    def _validate_range(self, value: Any, ctx: CharacteristicContext | None = None) -> None:  # noqa: ANN401  # Validates values of various numeric types
        """Validate value is within min/max range from both class attributes and descriptors."""
        # Check class-level validation attributes first
        if self.min_value is not None and value < self.min_value:
            raise ValueRangeError("value", value, self.min_value, self.max_value)
        if self.max_value is not None and value > self.max_value:
            raise ValueRangeError("value", value, self.min_value, self.max_value)

        # Check descriptor-defined valid range if available
        if isinstance(value, (int, float)):
            valid_range = self.get_valid_range_from_context(ctx)
            if valid_range:
                min_val, max_val = valid_range
                if not min_val <= value <= max_val:
                    raise ValueRangeError("value", value, min_val, max_val)

    def _validate_type(self, value: Any) -> None:  # noqa: ANN401  # Validates values of various types
        """Validate value type matches expected_type if specified."""
        if self.expected_type is not None and not isinstance(value, self.expected_type):
            raise TypeError(f"expected type {self.expected_type.__name__}, got {type(value).__name__}")

    def _validate_length(self, data: bytes | bytearray) -> None:
        """Validate data length meets requirements."""
        length = len(data)
        if self.expected_length is not None and length != self.expected_length:
            raise InsufficientDataError("characteristic_data", data, self.expected_length)
        if self.min_length is not None and length < self.min_length:
            raise InsufficientDataError("characteristic_data", data, self.min_length)
        if self.max_length is not None and length > self.max_length:
            raise ValueError(f"Maximum {self.max_length} bytes allowed, got {length}")

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
    ) -> CharacteristicDataProtocol | None:
        """Find a characteristic in a context by name or class.

        Args:
            ctx: Context containing other characteristics.
            characteristic_name: Enum, string name, or characteristic class.

        Returns:
            Characteristic data if found, None otherwise.

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

    def _is_parse_trace_enabled(self) -> bool:
        """Check if parse trace is enabled via environment variable or instance attribute.

        Returns:
            True if parse tracing is enabled, False otherwise

        Environment Variables:
            BLUETOOTH_SIG_ENABLE_PARSE_TRACE: Set to "0", "false", or "no" to disable

        Instance Attributes:
            _enable_parse_trace: Set to False to disable tracing for this instance
        """
        # Check environment variable first
        env_value = os.getenv("BLUETOOTH_SIG_ENABLE_PARSE_TRACE", "").lower()
        if env_value in ("0", "false", "no"):
            return False

        if self._enable_parse_trace is False:
            return False

        # Default to enabled
        return True

    def parse_value(self, data: bytes | bytearray, ctx: CharacteristicContext | None = None) -> CharacteristicData:
        """Parse raw characteristic data into structured value with validation.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context with descriptors and other characteristics

        Returns:
            CharacteristicData object with parsed value

        """
        # Convert to bytearray for internal processing
        data_bytes = bytearray(data)
        enable_trace = self._is_parse_trace_enabled()
        parse_trace: list[str] = []
        if enable_trace:
            parse_trace = ["Starting parse"]
        field_errors: list[FieldError] = []

        try:
            if enable_trace:
                parse_trace.append(f"Validating data length (got {len(data_bytes)} bytes)")
            self._validate_length(data_bytes)
            if enable_trace:
                parse_trace.append("Decoding value")
            parsed_value = self.decode_value(data_bytes, ctx)
            if enable_trace:
                parse_trace.append("Validating range")
            self._validate_range(parsed_value, ctx)
            if enable_trace:
                parse_trace.append("Validating type")
            self._validate_type(parsed_value)
            if enable_trace:
                parse_trace.append("completed successfully")
            return CharacteristicData(
                info=self._info,
                value=parsed_value,
                raw_data=bytes(data),
                parse_success=True,
                error_message="",
                field_errors=field_errors,
                parse_trace=parse_trace,
                descriptors={},
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            if enable_trace:
                if isinstance(e, ParseFieldError):
                    parse_trace.append(f"Field error: {str(e)}")
                    # Extract field error information
                    field_error = FieldError(
                        field=e.field,
                        reason=e.field_reason,
                        offset=e.offset,
                        raw_slice=bytes(e.data) if hasattr(e, "data") else None,
                    )
                    field_errors.append(field_error)
                else:
                    parse_trace.append(f"Parse failed: {str(e)}")
            return CharacteristicData(
                info=self._info,
                value=None,
                raw_data=bytes(data),
                parse_success=False,
                error_message=str(e),
                field_errors=field_errors,
                parse_trace=parse_trace,
                descriptors={},
            )

    def get_descriptors_from_context(self, ctx: CharacteristicContext | None) -> dict[str, Any]:
        """Extract descriptor data from the parsing context.

        Args:
            ctx: The characteristic context containing descriptor information

        Returns:
            Dictionary mapping descriptor UUIDs to DescriptorData objects
        """
        if not ctx or not ctx.descriptors:
            return {}

        # Return a copy of the descriptors from context
        return dict(ctx.descriptors)

    def encode_value(self, data: Any) -> bytearray:  # noqa: ANN401  # Encodes various value types (int, float, dataclass, etc.)
        """Encode the characteristic's value to raw bytes.

        If _template is set , uses the template's encode_value method.
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
        """Get the unit of measurement from _info."""
        return self._info.unit

    @property
    def properties(self) -> list[GattProperty]:
        """Get the GATT properties from _info."""
        return self._info.properties

    @property
    def size(self) -> int | None:
        """Get the size in bytes for this characteristic from YAML specifications.

        Returns the field size from YAML automation if available, otherwise None.
        This is useful for determining the expected data length for parsing
        and encoding.

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
        """Get the value type from _info."""
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

    # Descriptor support methods

    def add_descriptor(self, descriptor: BaseDescriptor) -> None:
        """Add a descriptor to this characteristic.

        Args:
            descriptor: The descriptor instance to add
        """
        self._descriptors[str(descriptor.uuid)] = descriptor

    def get_descriptor(self, uuid: str | BluetoothUUID) -> BaseDescriptor | None:
        """Get a descriptor by UUID.

        Args:
            uuid: Descriptor UUID (string or BluetoothUUID)

        Returns:
            Descriptor instance if found, None otherwise
        """
        # Convert to BluetoothUUID for consistent handling
        if isinstance(uuid, str):
            try:
                uuid_obj = BluetoothUUID(uuid)
            except ValueError:
                return None
        else:
            uuid_obj = uuid

        return self._descriptors.get(uuid_obj.dashed_form)

    def get_descriptors(self) -> dict[str, BaseDescriptor]:
        """Get all descriptors for this characteristic.

        Returns:
            Dict mapping descriptor UUID strings to descriptor instances
        """
        return self._descriptors.copy()

    def get_cccd(self) -> BaseDescriptor | None:
        """Get the Client Characteristic Configuration Descriptor (CCCD).

        Returns:
            CCCD descriptor instance if present, None otherwise
        """
        return self.get_descriptor(CCCDDescriptor().uuid)

    def can_notify(self) -> bool:
        """Check if this characteristic supports notifications.

        Returns:
            True if the characteristic has a CCCD descriptor, False otherwise
        """
        return self.get_cccd() is not None

    def get_descriptor_from_context(
        self, ctx: CharacteristicContext | None, descriptor_class: type[BaseDescriptor]
    ) -> DescriptorData | None:
        """Get a descriptor of the specified type from the context.

        Args:
            ctx: Characteristic context containing descriptors
            descriptor_class: The descriptor class to look for (e.g., ValidRangeDescriptor)

        Returns:
            DescriptorData if found, None otherwise
        """
        if not ctx or not ctx.descriptors:
            return None

        # Get the UUID from the descriptor class
        try:
            descriptor_instance = descriptor_class()
            descriptor_uuid = str(descriptor_instance.uuid)
        except (ValueError, TypeError, AttributeError):
            # If we can't create the descriptor instance, return None
            return None

        return ctx.descriptors.get(descriptor_uuid)

    def get_valid_range_from_context(
        self, ctx: CharacteristicContext | None = None
    ) -> tuple[int | float, int | float] | None:
        """Get valid range from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            Tuple of (min, max) values if Valid Range descriptor present, None otherwise
        """
        descriptor_data = self.get_descriptor_from_context(ctx, ValidRangeDescriptor)
        if descriptor_data and descriptor_data.value:
            return descriptor_data.value.min_value, descriptor_data.value.max_value
        return None

    def get_presentation_format_from_context(
        self, ctx: CharacteristicContext | None = None
    ) -> CharacteristicPresentationFormatData | None:
        """Get presentation format from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            CharacteristicPresentationFormatData if present, None otherwise
        """
        descriptor_data = self.get_descriptor_from_context(ctx, CharacteristicPresentationFormatDescriptor)
        if descriptor_data and descriptor_data.value:
            return descriptor_data.value  # type: ignore[no-any-return]
        return None

    def get_user_description_from_context(self, ctx: CharacteristicContext | None = None) -> str | None:
        """Get user description from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            User description string if present, None otherwise
        """
        descriptor_data = self.get_descriptor_from_context(ctx, CharacteristicUserDescriptionDescriptor)
        if descriptor_data and descriptor_data.value:
            return descriptor_data.value.description  # type: ignore[no-any-return]
        return None

    def validate_value_against_descriptor_range(
        self, value: int | float, ctx: CharacteristicContext | None = None
    ) -> bool:
        """Validate a value against descriptor-defined valid range.

        Args:
            value: Value to validate
            ctx: Characteristic context containing descriptors

        Returns:
            True if value is within valid range or no range defined, False otherwise
        """
        valid_range = self.get_valid_range_from_context(ctx)
        if valid_range is None:
            return True  # No range constraint, value is valid

        min_val, max_val = valid_range
        return min_val <= value <= max_val

    def enhance_error_message_with_descriptors(
        self, base_message: str, ctx: CharacteristicContext | None = None
    ) -> str:
        """Enhance error message with descriptor information for better debugging.

        Args:
            base_message: Original error message
            ctx: Characteristic context containing descriptors

        Returns:
            Enhanced error message with descriptor context
        """
        enhancements = []

        # Add valid range info if available
        valid_range = self.get_valid_range_from_context(ctx)
        if valid_range:
            min_val, max_val = valid_range
            enhancements.append(f"Valid range: {min_val}-{max_val}")

        # Add user description if available
        user_desc = self.get_user_description_from_context(ctx)
        if user_desc:
            enhancements.append(f"Description: {user_desc}")

        # Add presentation format info if available
        pres_format = self.get_presentation_format_from_context(ctx)
        if pres_format:
            enhancements.append(f"Format: {pres_format.format} ({pres_format.unit})")

        if enhancements:
            return f"{base_message} ({'; '.join(enhancements)})"
        return base_message

    def get_byte_order_hint(self) -> str:
        """Get byte order hint (Bluetooth SIG uses little-endian by convention)."""
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

    @classmethod
    def get_configured_info(cls) -> CharacteristicInfo | None:
        """Get the class-level configured CharacteristicInfo.

        Returns:
            CharacteristicInfo if configured, None otherwise

        """
        return cls._configured_info

    # pylint: disable=duplicate-code
    # NOTE: __init_subclass__ and __init__ patterns are intentionally similar to CustomBaseService.
    # This is by design - both custom characteristic and service classes need identical validation
    # and info management patterns. Consolidation not possible due to different base types and info types.
    def __init_subclass__(cls, allow_sig_override: bool = False, **kwargs: Any) -> None:  # noqa: ANN401  # Receives subclass kwargs
        """Automatically set up _info if provided as class attribute.

        Args:
            allow_sig_override: Set to True when intentionally overriding SIG UUIDs.
            **kwargs: Additional subclass keyword arguments passed by callers or
                metaclasses; these are accepted for compatibility and ignored
                unless explicitly handled.

        Raises:
            ValueError: If class uses SIG UUID without override permission.

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
        final_info = info or self.__class__.get_configured_info()

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
        else:
            configured_info = self.__class__.get_configured_info()
            if configured_info:
                self._info = configured_info
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
                value_type=info.value_type,
                properties=info.properties or [],
            )

        super().__init__(info=info)

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> bytes:  # Context type varies
        """Return raw bytes for unknown characteristics.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context (ignored)

        Returns:
            Raw bytes as-is

        """
        return bytes(data)

    def encode_value(self, data: Any) -> bytearray:  # noqa: ANN401  # Accepts bytes-like objects
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
