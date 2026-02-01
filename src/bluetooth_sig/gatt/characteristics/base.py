"""Base class for GATT characteristics.

This module implements the core characteristic parsing and encoding system for
Bluetooth GATT characteristics, following official Bluetooth SIG specifications.

Architecture
============

The implementation uses a multi-stage pipeline for parsing and encoding:

**Parsing Pipeline (parse_value):**
  1. Length validation (pre-decode)
  2. Raw integer extraction (little-endian per Bluetooth spec)
  3. Special value detection (sentinel values like 0x8000)
  4. Value decoding (via template or subclass override)
  5. Range validation (post-decode)
  6. Type validation

**Encoding Pipeline (build_value):**
  1. Type validation
  2. Range validation
  3. Value encoding (via template or subclass override)
  4. Length validation (post-encode)

YAML Metadata Resolution
=========================

Characteristic metadata is automatically resolved from Bluetooth SIG YAML specifications:

- UUID, name, value type from assigned numbers registry
- Units, resolution, and scaling factors (M * 10^d + b formula)
- Special sentinel values (e.g., 0x8000 = "value is not known")
- Validation ranges and length constraints

Manual overrides (_manual_unit, _special_values, etc.) should only be used for:
- Fixing incomplete or incorrect SIG specifications
- Custom characteristics not in official registry
- Performance optimizations

Template Composition
====================

Characteristics use templates for reusable parsing logic via composition:

    class TemperatureCharacteristic(BaseCharacteristic):
        _template = Sint16Template(resolution=0.01, unit="°C")
        # No need to override decode_value() - template handles it

Subclasses only override decode_value() for custom logic that templates
cannot handle. Templates take priority over YAML-derived extractors.

Validation Sources (Priority Order)
===================================

1. **Descriptor Valid Range** - Device-reported constraints (highest priority)
2. **Class-level Attributes** - Characteristic spec defaults (min_value, max_value)
3. **YAML-derived Ranges** - Bluetooth SIG specification ranges (fallback)

Special Values
==============

Sentinel values (like 0x8000 for "unknown") bypass range and type validation
since they represent non-numeric states. The gss_special_values property
handles both unsigned (0x8000) and signed (-32768) interpretations for
compatibility with different parsing contexts.

Byte Order
==========

All multi-byte values use little-endian encoding per Bluetooth Core Specification.
"""
# pylint: disable=too-many-lines

from __future__ import annotations

import os
import re
from abc import ABC, ABCMeta
from functools import cached_property, lru_cache
from typing import Any, ClassVar, Generic, TypeVar

import msgspec

from ...registry.uuids.units import units_registry
from ...types import (
    CharacteristicInfo,
    SpecialValueResult,
    SpecialValueRule,
    SpecialValueType,
    classify_special_value,
)
from ...types import ParseFieldError as FieldError
from ...types.data_types import ValidationAccumulator
from ...types.gatt_enums import CharacteristicName, DataType, GattProperty, ValueType
from ...types.registry import CharacteristicSpec
from ...types.registry.descriptor_types import DescriptorData
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..descriptor_utils import enhance_error_message_with_descriptors as _enhance_error_message
from ..descriptor_utils import get_descriptor_from_context as _get_descriptor
from ..descriptor_utils import get_presentation_format_from_context as _get_presentation_format
from ..descriptor_utils import get_user_description_from_context as _get_user_description
from ..descriptor_utils import get_valid_range_from_context as _get_valid_range
from ..descriptor_utils import validate_value_against_descriptor_range as _validate_value_range
from ..descriptors import BaseDescriptor
from ..descriptors.cccd import CCCDDescriptor
from ..descriptors.characteristic_presentation_format import CharacteristicPresentationFormatData
from ..exceptions import (
    CharacteristicEncodeError,
    CharacteristicParseError,
    ParseFieldError,
    SpecialValueDetectedError,
    UUIDResolutionError,
)
from ..resolver import CharacteristicRegistrySearch, NameNormalizer, NameVariantGenerator
from ..special_values_resolver import SpecialValueResolver
from ..uuid_registry import uuid_registry
from .templates import CodingTemplate
from .utils.extractors import get_extractor

# Type variable for generic characteristic return types
T = TypeVar("T")


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
    def resolve_for_class(char_class: type[BaseCharacteristic[Any]]) -> CharacteristicInfo:
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
    def resolve_yaml_spec_for_class(char_class: type[BaseCharacteristic[Any]]) -> CharacteristicSpec | None:
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
        yaml_spec: CharacteristicSpec, char_class: type[BaseCharacteristic[Any]]
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
        )

    @staticmethod
    def resolve_from_registry(char_class: type[BaseCharacteristic[Any]]) -> CharacteristicInfo | None:
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
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class BaseCharacteristic(ABC, Generic[T], metaclass=CharacteristicMeta):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Base class for all GATT characteristics.

    Generic over T, the return type of _decode_value().

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

            def _decode_value(self, data: bytearray) -> int:
                # Just parse - validation happens automatically in parse_value
                return DataParser.parse_int16(data, 0, signed=False)

        # Before: BatteryLevelCharacteristic with hardcoded validation
        # class BatteryLevelCharacteristic(BaseCharacteristic):
        #     def _decode_value(self, data: bytearray) -> int:
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
        #     def _decode_value(self, data: bytearray) -> int:
        #         return data[0]  # Validation happens automatically
    """

    # Explicit class attributes with defaults (replaces getattr usage)
    _characteristic_name: str | None = None
    _manual_unit: str | None = None
    _manual_value_type: ValueType | str | None = None
    _manual_size: int | None = None
    _is_template: bool = False

    min_value: int | float | None = None
    max_value: int | float | None = None
    expected_length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    allow_variable_length: bool = False
    expected_type: type | None = None

    _template: CodingTemplate[T] | None = None

    _allows_sig_override = False

    _required_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = []  # Dependencies that MUST be present
    _optional_dependencies: ClassVar[
        list[type[BaseCharacteristic[Any]]]
    ] = []  # Dependencies that enrich parsing when available

    # Parse trace control (for performance tuning)
    # Can be configured via BLUETOOTH_SIG_ENABLE_PARSE_TRACE environment variable
    # Set to "0", "false", or "no" to disable trace collection
    _enable_parse_trace: bool = True  # Default: enabled

    # Special value handling (GSS-derived)
    # Manual override for special values when GSS spec is incomplete/wrong.
    # Format: {raw_value: meaning_string}. GSS values are used by default.
    _special_values: dict[int, str] | None = None

    def __init__(
        self,
        info: CharacteristicInfo | None = None,
        validation: ValidationConfig | None = None,
        properties: list[GattProperty] | None = None,
    ) -> None:
        """Initialize characteristic with structured configuration.

        Args:
            info: Complete characteristic information (optional for SIG characteristics)
            validation: Validation constraints configuration (optional)
            properties: Runtime BLE properties discovered from device (optional)

        """
        # Store provided info or None (will be resolved in __post_init__)
        self._provided_info = info

        # Instance variables (will be set in __post_init__)
        self._info: CharacteristicInfo
        self._spec: CharacteristicSpec | None = None

        # Runtime properties (from actual device, not YAML)
        self.properties: list[GattProperty] = properties if properties is not None else []

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

        # Last parsed value for caching/debugging
        self.last_parsed: T | None = None

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

        # Resolve YAML spec for access to detailed metadata
        self._spec = self._resolve_yaml_spec()
        spec_rules: dict[int, SpecialValueRule] = {}
        for raw, meaning in self.gss_special_values.items():
            spec_rules[raw] = SpecialValueRule(
                raw_value=raw, meaning=meaning, value_type=classify_special_value(meaning)
            )

        class_rules: dict[int, SpecialValueRule] = {}
        if self._special_values is not None:
            for raw, meaning in self._special_values.items():
                class_rules[raw] = SpecialValueRule(
                    raw_value=raw, meaning=meaning, value_type=classify_special_value(meaning)
                )

        self._special_resolver = SpecialValueResolver(spec_rules=spec_rules, class_rules=class_rules)

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

        # Feature characteristics are bitfields and should be BITFIELD
        if "Feature" in class_name or "Feature" in char_name:
            return ValueType.BITFIELD

        # Check if this is a multi-field characteristic (complex structure)
        if self._spec and hasattr(self._spec, "structure") and len(self._spec.structure) > 1:
            return ValueType.VARIOUS

        # Common simple value characteristics
        simple_int_patterns = ["Level", "Count", "Index", "ID", "Appearance"]
        if any(pattern in class_name or pattern in char_name for pattern in simple_int_patterns):
            return ValueType.INT

        simple_string_patterns = ["Name", "Description", "Text", "String"]
        if any(pattern in class_name or pattern in char_name for pattern in simple_string_patterns):
            return ValueType.STRING

        # Default fallback for complex characteristics
        return ValueType.VARIOUS

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
    def spec(self) -> CharacteristicSpec | None:
        """Get the full GSS specification with description and detailed metadata."""
        return self._spec

    @property
    def name(self) -> str:
        """Get the characteristic name from _info."""
        return self._info.name

    @property
    def description(self) -> str:
        """Get the characteristic description from GSS specification."""
        return self._spec.description if self._spec and self._spec.description else ""

    @property
    def display_name(self) -> str:
        """Get the display name for this characteristic.

        Uses explicit _characteristic_name if set, otherwise falls back
        to class name.
        """
        return self._characteristic_name or self.__class__.__name__

    @cached_property
    def gss_special_values(self) -> dict[int, str]:
        """Get special values from GSS specification.

        Extracts all special value definitions (e.g., 0x8000="value is not known")
        from the GSS YAML specification for this characteristic.

        GSS stores values as unsigned hex (e.g., 0x8000). For signed types,
        this method also includes the signed interpretation so lookups work
        with both parsed signed values and raw unsigned values.

        Returns:
            Dictionary mapping raw integer values to their human-readable meanings.
            Includes both unsigned and signed interpretations for applicable values.
        """
        # extract special values from YAML
        if not self._spec or not hasattr(self._spec, "structure") or not self._spec.structure:
            return {}

        result: dict[int, str] = {}
        for field in self._spec.structure:  # pylint: disable=too-many-nested-blocks  # Spec requires nested iteration for special values
            for sv in field.special_values:
                unsigned_val = sv.raw_value
                result[unsigned_val] = sv.meaning

                # For signed types, add the signed equivalent based on common bit widths.
                # This handles cases like 0x8000 (32768) -> -32768 for sint16.
                if self.is_signed_from_yaml():
                    for bits in (8, 16, 24, 32):
                        max_unsigned = (1 << bits) - 1
                        sign_bit = 1 << (bits - 1)
                        if sign_bit <= unsigned_val <= max_unsigned:
                            # This value would be negative when interpreted as signed
                            signed_val = unsigned_val - (1 << bits)
                            if signed_val not in result:
                                result[signed_val] = sv.meaning
        return result

    def is_special_value(self, raw_value: int) -> bool:
        """Check if a raw value is a special sentinel value.

        Checks both manual overrides (_special_values class variable) and
        GSS-derived special values, with manual taking precedence.

        Args:
            raw_value: The raw integer value to check.

        Returns:
            True if this is a special sentinel value, False otherwise.
        """
        return self._special_resolver.is_special(raw_value)

    def get_special_value_meaning(self, raw_value: int) -> str | None:
        """Get the human-readable meaning of a special value.

        Args:
            raw_value: The raw integer value to look up.

        Returns:
            The meaning string (e.g., "value is not known"), or None if not special.
        """
        res = self._special_resolver.resolve(raw_value)
        return res.meaning if res is not None else None

    def get_special_value_type(self, raw_value: int) -> SpecialValueType | None:
        """Get the category of a special value.

        Args:
            raw_value: The raw integer value to classify.

        Returns:
            The SpecialValueType category, or None if not a special value.
        """
        res = self._special_resolver.resolve(raw_value)
        return res.value_type if res is not None else None

    @classmethod
    def _normalize_dependency_class(cls, dep_class: type[BaseCharacteristic[Any]]) -> str | None:
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
        """Resolve dependency class references to canonical UUID strings.

        Performance: Returns list[str] instead of list[BluetoothUUID] because
        these are compared against dict[str, ...] keys in hot paths.
        """
        dependency_classes: list[type[BaseCharacteristic[Any]]] = []

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
        """Get resolved required dependency UUID strings.

        Performance: Returns list[str] for efficient comparison with dict keys.
        """
        if self._resolved_required_dependencies is None:
            self._resolved_required_dependencies = self._resolve_dependencies("_required_dependencies")

        return list(self._resolved_required_dependencies)

    @property
    def optional_dependencies(self) -> list[str]:
        """Get resolved optional dependency UUID strings.

        Performance: Returns list[str] for efficient comparison with dict keys.
        """
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
        # Check for _info attribute first (custom characteristics)
        if hasattr(cls, "_info"):
            info: CharacteristicInfo = cls._info  # Custom characteristics may have _info
            try:
                return info.uuid
            except AttributeError:
                pass

        # Try cross-file resolution for SIG characteristics
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
        except (ValueError, KeyError, AttributeError, TypeError):
            # Registry resolution can fail for various reasons:
            # - ValueError: Invalid UUID format
            # - KeyError: Characteristic not in registry
            # - AttributeError: Missing expected attributes
            # - TypeError: Type mismatch in resolution
            return None
        else:
            return registry_info.uuid if registry_info else None

    @classmethod
    def matches_uuid(cls, uuid: str | BluetoothUUID) -> bool:
        """Check if this characteristic matches the given UUID."""
        try:
            class_uuid = cls._resolve_class_uuid()
            if class_uuid is None:
                return False
            input_uuid = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)
        except ValueError:
            return False
        else:
            return class_uuid == input_uuid

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> T:
        """Internal parse the characteristic's raw value with no validation.

        This is expected to be called from parse_value() which handles validation.

        If _template is set, uses the template's decode_value method.
        Otherwise, subclasses must override this method.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context information for parsing
            validate: Whether to validate ranges (default True)
            validate: Whether to validate ranges (default True)

        Returns:
            Parsed value in the appropriate type

        Raises:
            NotImplementedError: If no template is set and subclass doesn't override

        """
        if self._template is not None:
            return self._template.decode_value(  # pylint: disable=protected-access
                data, offset=0, ctx=ctx, validate=validate
            )
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override decode_value()")

    def _validate_range(
        self,
        value: Any,  # noqa: ANN401  # Validates values of various numeric types
        ctx: CharacteristicContext | None = None,
    ) -> ValidationAccumulator:  # pylint: disable=too-many-branches  # Multiple validation precedence levels per spec
        """Validate value is within min/max range from both class attributes and descriptors.

        Validation precedence:
        1. Descriptor Valid Range (if present in context) - most specific, device-reported
        2. Class-level validation attributes (min_value, max_value) - characteristic spec defaults
        3. YAML-derived value range from structure - Bluetooth SIG specification

        Args:
            value: The value to validate
            ctx: Optional characteristic context containing descriptors

        Returns:
            ValidationReport with errors if validation fails
        """
        result = ValidationAccumulator()

        # Skip validation for SpecialValueResult
        if isinstance(value, SpecialValueResult):
            return result

        # Skip validation for non-numeric types
        if not isinstance(value, (int, float)):
            return result

        # Check descriptor Valid Range first (takes precedence over class attributes)
        descriptor_range = self.get_valid_range_from_context(ctx) if ctx else None
        if descriptor_range is not None:
            min_val, max_val = descriptor_range
            if value < min_val or value > max_val:
                error_msg = (
                    f"Value {value} is outside valid range [{min_val}, {max_val}] "
                    f"(source: Valid Range descriptor for {self.name})"
                )
                if self.unit:
                    error_msg += f" [unit: {self.unit}]"
                result.add_error(error_msg)
            # Descriptor validation checked - skip class-level checks
            return result

        # Fall back to class-level validation attributes
        if self.min_value is not None and value < self.min_value:
            error_msg = (
                f"Value {value} is below minimum {self.min_value} "
                f"(source: class-level constraint for {self.__class__.__name__})"
            )
            if self.unit:
                error_msg += f" [unit: {self.unit}]"
            result.add_error(error_msg)
        if self.max_value is not None and value > self.max_value:
            error_msg = (
                f"Value {value} is above maximum {self.max_value} "
                f"(source: class-level constraint for {self.__class__.__name__})"
            )
            if self.unit:
                error_msg += f" [unit: {self.unit}]"
            result.add_error(error_msg)

        # Fall back to YAML-derived value range from structure
        # Use tolerance-based comparison for floating-point values due to precision loss in scaled types
        if self.min_value is None and self.max_value is None and self._spec and self._spec.structure:
            for field in self._spec.structure:
                yaml_range = field.value_range
                if yaml_range is not None:
                    min_val, max_val = yaml_range
                    # Use tolerance for floating-point comparison (common in scaled characteristics)
                    tolerance = max(abs(max_val - min_val) * 1e-9, 1e-9) if isinstance(value, float) else 0
                    if value < min_val - tolerance or value > max_val + tolerance:
                        yaml_source = f"{self._spec.name}" if self._spec.name else "YAML specification"
                        error_msg = (
                            f"Value {value} is outside allowed range [{min_val}, {max_val}] "
                            f"(source: Bluetooth SIG {yaml_source})"
                        )
                        if self.unit:
                            error_msg += f" [unit: {self.unit}]"
                        result.add_error(error_msg)
                    break  # Use first field with range found

        return result

    def _validate_type(self, value: Any) -> ValidationAccumulator:  # noqa: ANN401
        """Validate value type matches expected_type if specified.

        Args:
            value: The value to validate
            validate: Whether validation is enabled

        Returns:
            ValidationReport with errors if validation fails
        """
        result = ValidationAccumulator()

        if self.expected_type is not None and not isinstance(value, (self.expected_type, SpecialValueResult)):
            error_msg = (
                f"Type validation failed for {self.name}: "
                f"expected {self.expected_type.__name__}, got {type(value).__name__} "
                f"(value: {value})"
            )
            result.add_error(error_msg)
        return result

    def _validate_length(self, data: bytes | bytearray) -> ValidationAccumulator:
        """Validate data length meets requirements.

        Args:
            data: The data to validate

        Returns:
            ValidationReport with errors if validation fails
        """
        result = ValidationAccumulator()

        length = len(data)

        # Determine validation source for error context
        yaml_size = self.get_yaml_field_size()
        source_context = ""
        if yaml_size is not None:
            source_context = f" (YAML specification: {yaml_size} bytes)"
        elif self.expected_length is not None or self.min_length is not None or self.max_length is not None:
            source_context = f" (class-level constraint for {self.__class__.__name__})"

        if self.expected_length is not None and length != self.expected_length:
            error_msg = (
                f"Length validation failed for {self.name}: "
                f"expected exactly {self.expected_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        if self.min_length is not None and length < self.min_length:
            error_msg = (
                f"Length validation failed for {self.name}: "
                f"expected at least {self.min_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        if self.max_length is not None and length > self.max_length:
            error_msg = (
                f"Length validation failed for {self.name}: "
                f"expected at most {self.max_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        return result

    def _extract_raw_int(
        self,
        data: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
    ) -> int | None:
        """Extract raw integer from bytes using the extraction pipeline.

        Tries extraction in order of precedence:
        1. Template extractor (if _template with extractor is set)
        2. YAML-derived extractor (based on get_yaml_data_type())

        Args:
            data: Raw bytes to extract from.
            enable_trace: Whether to log trace messages.
            parse_trace: List to append trace messages to.

        Returns:
            Raw integer value, or None if no extractor is available.
        """
        # Priority 1: Template extractor
        if self._template is not None and self._template.extractor is not None:
            if enable_trace:
                parse_trace.append("Extracting raw integer via template extractor")
            raw_int = self._template.extractor.extract(data, offset=0)
            if enable_trace:
                parse_trace.append(f"Extracted raw_int: {raw_int}")
            return raw_int

        # Priority 2: YAML data type extractor
        yaml_type = self.get_yaml_data_type()
        if yaml_type is not None:
            extractor = get_extractor(yaml_type)
            if extractor is not None:
                if enable_trace:
                    parse_trace.append(f"Extracting raw integer via YAML type '{yaml_type}'")
                raw_int = extractor.extract(data, offset=0)
                if enable_trace:
                    parse_trace.append(f"Extracted raw_int: {raw_int}")
                return raw_int

        # No extractor available
        if enable_trace:
            parse_trace.append("No extractor available for raw_int extraction")
        return None

    def _pack_raw_int(self, raw: int) -> bytearray:
        """Pack a raw integer to bytes using template extractor or YAML extractor."""
        # Priority 1: template extractor
        if self._template is not None:
            extractor = getattr(self._template, "extractor", None)
            if extractor is not None:
                return bytearray(extractor.pack(raw))

        # Priority 2: YAML-derived extractor
        yaml_type = self.get_yaml_data_type()
        if yaml_type is not None:
            extractor = get_extractor(yaml_type)
            if extractor is not None:
                return bytearray(extractor.pack(raw))

        raise ValueError("No extractor available to pack raw integer for this characteristic")

    def _get_dependency_from_context(
        self,
        ctx: CharacteristicContext,
        dep_class: type[BaseCharacteristic[Any]],
    ) -> Any:  # noqa: ANN401  # Dependency type determined by dep_class at runtime
        """Get dependency from context using type-safe class reference.

        Note:
            Returns ``Any`` because the dependency type is determined at runtime
            by ``dep_class``. For type-safe access, the caller should know the
            expected type based on the class they pass in.

        Args:
            ctx: Characteristic context containing other characteristics
            dep_class: Dependency characteristic class to look up

        Returns:
            Parsed characteristic value if found in context, None otherwise.

        """
        # Resolve class to UUID
        dep_uuid = dep_class.get_class_uuid()
        if not dep_uuid:
            return None

        # Lookup in context by UUID (string key)
        if ctx.other_characteristics is None:
            return None
        return ctx.other_characteristics.get(str(dep_uuid))

    @staticmethod
    @lru_cache(maxsize=32)
    def _get_characteristic_uuid_by_name(
        characteristic_name: CharacteristicName | str,
    ) -> BluetoothUUID | None:
        """Get characteristic UUID by name using cached registry lookup."""
        # Convert enum to string value for registry lookup
        name_str = (
            characteristic_name.value if isinstance(characteristic_name, CharacteristicName) else characteristic_name
        )
        char_info = uuid_registry.get_characteristic_info(name_str)
        return char_info.uuid if char_info else None

    def get_context_characteristic(
        self,
        ctx: CharacteristicContext | None,
        characteristic_name: CharacteristicName | str | type[BaseCharacteristic[Any]],
    ) -> Any:  # noqa: ANN401  # Type determined by characteristic_name at runtime
        """Find a characteristic in a context by name or class.

        Note:
            Returns ``Any`` because the characteristic type is determined at
            runtime by ``characteristic_name``. For type-safe access, use direct
            characteristic class instantiation instead of this lookup method.

        Args:
            ctx: Context containing other characteristics.
            characteristic_name: Enum, string name, or characteristic class.

        Returns:
            Parsed characteristic value if found, None otherwise.

        """
        if not ctx or not ctx.other_characteristics:
            return None

        # Extract UUID from class if provided
        if isinstance(characteristic_name, type):
            # Class reference provided - try to get class-level UUID
            configured_info: CharacteristicInfo | None = getattr(characteristic_name, "_configured_info", None)
            if configured_info is not None:
                # Custom characteristic with explicit _configured_info
                char_uuid = configured_info.uuid
            else:
                # SIG characteristic: convert class name to SIG name and resolve via registry
                class_name: str = characteristic_name.__name__
                # Remove 'Characteristic' suffix
                name_without_suffix: str = class_name.replace("Characteristic", "")
                # Insert spaces before capital letters to get SIG name
                sig_name: str = re.sub(r"(?<!^)(?=[A-Z])", " ", name_without_suffix)
                # Look up UUID via registry
                resolved_uuid = self._get_characteristic_uuid_by_name(sig_name)
                if resolved_uuid is None:
                    return None
                char_uuid = resolved_uuid
        else:
            # Enum or string name
            resolved_uuid = self._get_characteristic_uuid_by_name(characteristic_name)
            if resolved_uuid is None:
                return None
            char_uuid = resolved_uuid

        return ctx.other_characteristics.get(str(char_uuid))

    def _check_special_value(self, raw_value: int) -> int | SpecialValueResult:
        """Check if raw value is a special sentinel value and return appropriate result.

        Args:
            raw_value: The raw integer value to check

        Returns:
            SpecialValueResult if raw_value is special, otherwise raw_value unchanged
        """
        res = self._special_resolver.resolve(raw_value)
        if res is not None:
            return res
        return raw_value

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

        # Return True unless explicitly disabled
        return self._enable_parse_trace is not False

    def _perform_parse_validation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        data_bytes: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
        validation: ValidationAccumulator,
        validate: bool,
    ) -> None:
        """Perform initial validation on parse data."""
        if not validate:
            return
        if enable_trace:
            parse_trace.append(f"Validating data length (got {len(data_bytes)} bytes)")
        length_validation = self._validate_length(data_bytes)
        validation.errors.extend(length_validation.errors)
        validation.warnings.extend(length_validation.warnings)
        if not length_validation.valid:
            raise ValueError("; ".join(length_validation.errors))

    def _extract_and_check_special_value(  # pylint: disable=unused-argument  # ctx used in get_valid_range_from_context by callers
        self, data_bytes: bytearray, enable_trace: bool, parse_trace: list[str], ctx: CharacteristicContext | None
    ) -> tuple[int | None, int | SpecialValueResult | None]:
        """Extract raw int and check for special values."""
        # Extract raw integer using the pipeline
        raw_int = self._extract_raw_int(data_bytes, enable_trace, parse_trace)

        # Check for special values if raw_int was extracted
        parsed_value = None
        if raw_int is not None:
            if enable_trace:
                parse_trace.append("Checking for special values")
            parsed_value = self._check_special_value(raw_int)
            if enable_trace:
                if isinstance(parsed_value, SpecialValueResult):
                    parse_trace.append(f"Found special value: {parsed_value}")
                else:
                    parse_trace.append("Not a special value, proceeding with decode")

        return raw_int, parsed_value

    def _decode_and_validate_value(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # All parameters necessary for decode/validate pipeline
        self,
        data_bytes: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
        ctx: CharacteristicContext | None,
        validation: ValidationAccumulator,
        validate: bool,
    ) -> T:
        """Decode value and perform validation.

        At this point, special values have already been handled by the caller.
        """
        if enable_trace:
            parse_trace.append("Decoding value")
        # Pass validate flag directly to template decode_value method
        decoded_value: T = self._decode_value(data_bytes, ctx, validate=validate)

        if validate:
            if enable_trace:
                parse_trace.append("Validating range")
            range_validation = self._validate_range(decoded_value, ctx)
            validation.errors.extend(range_validation.errors)
            validation.warnings.extend(range_validation.warnings)
            if not range_validation.valid:
                raise ValueError("; ".join(range_validation.errors))
            if enable_trace:
                parse_trace.append("Validating type")
            type_validation = self._validate_type(decoded_value)
            validation.errors.extend(type_validation.errors)
            validation.warnings.extend(type_validation.warnings)
            if not type_validation.valid:
                raise ValueError("; ".join(type_validation.errors))
        return decoded_value

    def parse_value(
        self, data: bytes | bytearray, ctx: CharacteristicContext | None = None, validate: bool = True
    ) -> T:
        """Parse characteristic data.

        Returns: Parsed value of type T
        Raises:
            SpecialValueDetectedError: Special sentinel (0x8000="unknown", 0x7FFFFFFF="NaN")
            CharacteristicParseError: Parse/validation failure
        """
        data_bytes = bytearray(data)
        enable_trace = self._is_parse_trace_enabled()
        parse_trace: list[str] = ["Starting parse"] if enable_trace else []
        field_errors: list[FieldError] = []
        validation = ValidationAccumulator()
        raw_int: int | None = None

        try:
            self._perform_parse_validation(data_bytes, enable_trace, parse_trace, validation, validate)
            raw_int, parsed_value = self._extract_and_check_special_value(data_bytes, enable_trace, parse_trace, ctx)
        except Exception as e:
            if enable_trace:
                parse_trace.append(f"Parse failed: {type(e).__name__}: {e}")
            raise CharacteristicParseError(
                message=str(e),
                name=self.name,
                uuid=self.uuid,
                raw_data=bytes(data),
                raw_int=raw_int,
                field_errors=field_errors,
                parse_trace=parse_trace,
                validation=validation,
            ) from e

        if isinstance(parsed_value, SpecialValueResult):
            if enable_trace:
                parse_trace.append(f"Detected special value: {parsed_value.meaning}")
            raise SpecialValueDetectedError(
                special_value=parsed_value, name=self.name, uuid=self.uuid, raw_data=bytes(data), raw_int=raw_int
            )

        try:
            decoded_value = self._decode_and_validate_value(
                data_bytes, enable_trace, parse_trace, ctx, validation, validate
            )
        except Exception as e:
            if enable_trace:
                parse_trace.append(f"Parse failed: {type(e).__name__}: {e}")
            if isinstance(e, ParseFieldError):
                field_errors.append(
                    FieldError(
                        field=e.field,
                        reason=e.field_reason,
                        offset=e.offset,
                        raw_slice=bytes(e.data) if hasattr(e, "data") else None,
                    )
                )
            raise CharacteristicParseError(
                message=str(e),
                name=self.name,
                uuid=self.uuid,
                raw_data=bytes(data),
                raw_int=raw_int,
                field_errors=field_errors,
                parse_trace=parse_trace,
                validation=validation,
            ) from e

        if enable_trace:
            parse_trace.append("Parse completed successfully")

        self.last_parsed = decoded_value
        return decoded_value

    def _encode_value(self, data: Any) -> bytearray:  # noqa: ANN401
        """Internal encode the characteristic's value to raw bytes with no validation.

        This is expected to called from build_value() after validation.

        If _template is set, uses the template's encode_value method.
        Otherwise, subclasses must override this method.

        This is a low-level method that performs no validation. For encoding
        with validation, use encode() instead.

        Args:
            data: Dataclass instance or value to encode

        Returns:
            Encoded bytes for characteristic write

        Raises:
            ValueError: If data is invalid for encoding
            NotImplementedError: If no template is set and subclass doesn't override

        """
        if self._template is not None:
            return self._template.encode_value(data)  # pylint: disable=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override encode_value()")

    def build_value(  # pylint: disable=too-many-branches
        self, data: T | SpecialValueResult, validate: bool = True
    ) -> bytearray:
        """Encode value or special value to characteristic bytes.

        Args:
            data: Value to encode (type T) or special value to encode
            validate: Enable validation (type, range, length checks)
                      Note: Special values bypass validation

        Returns:
            Encoded bytes ready for BLE write

        Raises:
            CharacteristicEncodeError: If encoding or validation fails

        Examples:
            # Normal value
            data = char.build_value(37.5)  # Returns: bytearray([0xAA, 0x0E])

            # Special value (for testing/simulation)
            from bluetooth_sig.types import SpecialValueResult, SpecialValueType
            special = SpecialValueResult(
                raw_value=0x8000,
                meaning="value is not known",
                value_type=SpecialValueType.NOT_KNOWN
            )
            data = char.build_value(special)  # Returns: bytearray([0x00, 0x80])

            # With validation disabled (for debugging)
            data = char.build_value(200.0, validate=False)  # Allows out-of-range

            # Error handling
            try:
                data = char.build_value(value)
            except CharacteristicEncodeError as e:
                print(f"Encode failed: {e}")

        """
        enable_trace = self._is_parse_trace_enabled()
        build_trace: list[str] = ["Starting build"] if enable_trace else []
        validation = ValidationAccumulator()

        # Special value encoding - bypass validation
        if isinstance(data, SpecialValueResult):
            if enable_trace:
                build_trace.append(f"Encoding special value: {data.meaning}")
            try:
                return self._pack_raw_int(data.raw_value)
            except Exception as e:
                raise CharacteristicEncodeError(
                    message=f"Failed to encode special value: {e}",
                    name=self.name,
                    uuid=self.uuid,
                    value=data,
                    validation=None,
                ) from e

        try:
            # Type validation
            if validate:
                if enable_trace:
                    build_trace.append("Validating type")
                type_validation = self._validate_type(data)
                validation.errors.extend(type_validation.errors)
                validation.warnings.extend(type_validation.warnings)
                if not type_validation.valid:
                    raise TypeError("; ".join(type_validation.errors))  # noqa: TRY301

            # Range validation for numeric types
            if validate and isinstance(data, (int, float)):
                if enable_trace:
                    build_trace.append("Validating range")
                range_validation = self._validate_range(data, ctx=None)
                validation.errors.extend(range_validation.errors)
                validation.warnings.extend(range_validation.warnings)
                if not range_validation.valid:
                    raise ValueError("; ".join(range_validation.errors))  # noqa: TRY301

            # Encode
            if enable_trace:
                build_trace.append("Encoding value")
            encoded = self._encode_value(data)

            # Length validation
            if validate:
                if enable_trace:
                    build_trace.append("Validating encoded length")
                length_validation = self._validate_length(encoded)
                validation.errors.extend(length_validation.errors)
                validation.warnings.extend(length_validation.warnings)
                if not length_validation.valid:
                    raise ValueError("; ".join(length_validation.errors))  # noqa: TRY301

            if enable_trace:
                build_trace.append("Build completed successfully")

        except Exception as e:
            if enable_trace:
                build_trace.append(f"Build failed: {type(e).__name__}: {e}")

            raise CharacteristicEncodeError(
                message=str(e),
                name=self.name,
                uuid=self.uuid,
                value=data,
                validation=validation,
            ) from e
        else:
            return encoded

    # -------------------- Encoding helpers for special values --------------------
    def encode_special(self, value_type: SpecialValueType) -> bytearray:
        """Encode a special value type to bytes (reverse lookup).

        Raises ValueError if no raw value of that type is defined for this characteristic.
        """
        raw = self._special_resolver.get_raw_for_type(value_type)
        if raw is None:
            raise ValueError(f"No special value of type {value_type.name} defined for this characteristic")
        return self._pack_raw_int(raw)

    def encode_special_by_meaning(self, meaning: str) -> bytearray:
        """Encode a special value by a partial meaning string match.

        Raises ValueError if no matching special value is found.
        """
        raw = self._special_resolver.get_raw_for_meaning(meaning)
        if raw is None:
            raise ValueError(f"No special value matching '{meaning}' defined for this characteristic")
        return self._pack_raw_int(raw)

    @property
    def unit(self) -> str:
        """Get the unit of measurement from _info.

        Returns empty string for characteristics without units (e.g., bitfields).
        """
        return self._info.unit or ""

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
        return self._spec.data_type if self._spec else None

    def get_yaml_field_size(self) -> int | None:
        """Get the field size in bytes from YAML automation."""
        field_size = self._spec.field_size if self._spec else None
        if field_size and isinstance(field_size, str) and field_size.isdigit():
            return int(field_size)
        return None

    def get_yaml_unit_id(self) -> str | None:
        """Get the Bluetooth SIG unit identifier from YAML automation."""
        return self._spec.unit_id if self._spec else None

    def get_yaml_resolution_text(self) -> str | None:
        """Get the resolution description text from YAML automation."""
        return self._spec.resolution_text if self._spec else None

    def is_signed_from_yaml(self) -> bool:
        """Determine if the data type is signed based on YAML automation."""
        data_type = self.get_yaml_data_type()
        if not data_type:
            return False
        # Check for signed types: signed integers, medical floats, and standard floats
        return data_type.startswith("sint") or data_type in ("medfloat16", "medfloat32", "float32", "float64")

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
        return _get_descriptor(ctx, descriptor_class)

    def get_valid_range_from_context(
        self, ctx: CharacteristicContext | None = None
    ) -> tuple[int | float, int | float] | None:
        """Get valid range from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            Tuple of (min, max) values if Valid Range descriptor present, None otherwise
        """
        return _get_valid_range(ctx)

    def get_presentation_format_from_context(
        self, ctx: CharacteristicContext | None = None
    ) -> CharacteristicPresentationFormatData | None:
        """Get presentation format from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            CharacteristicPresentationFormatData if present, None otherwise
        """
        return _get_presentation_format(ctx)

    def get_user_description_from_context(self, ctx: CharacteristicContext | None = None) -> str | None:
        """Get user description from descriptor context if available.

        Args:
            ctx: Characteristic context containing descriptors

        Returns:
            User description string if present, None otherwise
        """
        return _get_user_description(ctx)

    def validate_value_against_descriptor_range(self, value: float, ctx: CharacteristicContext | None = None) -> bool:
        """Validate a value against descriptor-defined valid range.

        Args:
            value: Value to validate
            ctx: Characteristic context containing descriptors

        Returns:
            True if value is within valid range or no range defined, False otherwise
        """
        return _validate_value_range(value, ctx)

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
        return _enhance_error_message(base_message, ctx)

    def get_byte_order_hint(self) -> str:
        """Get byte order hint (Bluetooth SIG uses little-endian by convention)."""
        return "little"
