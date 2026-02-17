"""Base class for GATT characteristics.

Implements the core parsing and encoding system for Bluetooth GATT
characteristics following official Bluetooth SIG specifications.

See :mod:`.characteristic_meta` for infrastructure classes
(``SIGCharacteristicResolver``, ``CharacteristicMeta``, ``ValidationConfig``).
See :mod:`.pipeline` for the multi-stage parse/encode pipeline.
See :mod:`.role_classifier` for characteristic role inference.
"""

from __future__ import annotations

from abc import ABC
from functools import cached_property
from typing import Any, ClassVar, Generic, TypeVar

from ...types import (
    CharacteristicInfo,
    SpecialValueResult,
    SpecialValueRule,
    SpecialValueType,
    classify_special_value,
)
from ...types.gatt_enums import CharacteristicRole, GattProperty, ValueType
from ...types.registry import CharacteristicSpec
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..descriptors import BaseDescriptor
from ..special_values_resolver import SpecialValueResolver
from .characteristic_meta import CharacteristicMeta, SIGCharacteristicResolver
from .characteristic_meta import ValidationConfig as ValidationConfig  # noqa: PLC0414  # explicit re-export
from .context_lookup import ContextLookupMixin
from .descriptor_mixin import DescriptorMixin
from .pipeline import CharacteristicValidator, EncodePipeline, ParsePipeline
from .role_classifier import classify_role
from .templates import CodingTemplate

# Type variable for generic characteristic return types
T = TypeVar("T")


class BaseCharacteristic(ContextLookupMixin, DescriptorMixin, ABC, Generic[T], metaclass=CharacteristicMeta):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Base class for all GATT characteristics.

    Generic over *T*, the return type of ``_decode_value()``.

    Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML
    specifications.  Supports manual overrides via ``_manual_unit`` and
    ``_manual_value_type`` attributes.

    Validation Attributes (optional class-level declarations):
        min_value / max_value: Allowed numeric range.
        expected_length / min_length / max_length: Byte-length constraints.
        allow_variable_length: Accept variable length data.
        expected_type: Expected Python type for parsed values.
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

    # Role classification (computed once per concrete subclass)
    # Subclasses can set _manual_role to bypass the heuristic entirely.
    _manual_role: ClassVar[CharacteristicRole | None] = None
    _cached_role: ClassVar[CharacteristicRole | None] = None

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

        # Pipeline composition — validator is shared by parse and encode pipelines
        self._validator = CharacteristicValidator(self)
        self._parse_pipeline = ParsePipeline(self, self._validator)
        self._encode_pipeline = EncodePipeline(self, self._validator)

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
    def role(self) -> CharacteristicRole:
        """Classify the characteristic's purpose from SIG spec metadata.

        Override via ``_manual_role`` class variable, or the heuristic in
        :func:`.role_classifier.classify_role` is used.  Result is cached
        per concrete subclass.
        """
        cls = type(self)
        if cls._cached_role is None:
            if cls._manual_role is not None:
                cls._cached_role = cls._manual_role
            else:
                cls._cached_role = classify_role(self.name, self.value_type, self.unit, self._spec)
        return cls._cached_role

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
        """Decode raw bytes into the characteristic's typed value.

        Called internally by :meth:`parse_value` after pipeline validation.
        Uses *_template* when set; subclasses override for custom logic.
        """
        if self._template is not None:
            return self._template.decode_value(  # pylint: disable=protected-access
                data, offset=0, ctx=ctx, validate=validate
            )
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override decode_value()")

    def parse_value(
        self, data: bytes | bytearray, ctx: CharacteristicContext | None = None, validate: bool = True
    ) -> T:
        """Parse characteristic data.

        Delegates to :class:`ParsePipeline` for the multi-stage pipeline
        (length validation → raw int extraction → special value detection →
        decode → range/type validation).

        Returns:
            Parsed value of type T.

        Raises:
            SpecialValueDetectedError: Special sentinel (0x8000="unknown", 0x7FFFFFFF="NaN")
            CharacteristicParseError: Parse/validation failure

        """
        decoded: T = self._parse_pipeline.run(data, ctx, validate)
        self.last_parsed = decoded
        return decoded

    def _encode_value(self, data: Any) -> bytearray:  # noqa: ANN401
        """Encode a typed value into raw bytes (no validation).

        Called internally by :meth:`build_value` after pipeline validation.
        Uses *_template* when set; subclasses override for custom logic.
        """
        if self._template is not None:
            return self._template.encode_value(data)  # pylint: disable=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} must either set _template or override encode_value()")

    def build_value(self, data: T | SpecialValueResult, validate: bool = True) -> bytearray:
        """Encode value or special value to characteristic bytes.

        Delegates to :class:`EncodePipeline` for the multi-stage pipeline
        (type validation → range validation → encode → length validation).

        Args:
            data: Value to encode (type T) or :class:`SpecialValueResult`.
            validate: Enable validation (type, range, length checks).

        Returns:
            Encoded bytes ready for BLE write.

        Raises:
            CharacteristicEncodeError: If encoding or validation fails.

        """
        return self._encode_pipeline.run(data, validate)

    # -------------------- Encoding helpers for special values --------------------
    def encode_special(self, value_type: SpecialValueType) -> bytearray:
        """Encode a special value type to bytes (reverse lookup).

        Raises ValueError if no raw value of that type is defined for this characteristic.
        """
        return self._encode_pipeline.encode_special(value_type)

    def encode_special_by_meaning(self, meaning: str) -> bytearray:
        """Encode a special value by a partial meaning string match.

        Raises ValueError if no matching special value is found.
        """
        return self._encode_pipeline.encode_special_by_meaning(meaning)

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

    def get_byte_order_hint(self) -> str:
        """Get byte order hint (Bluetooth SIG uses little-endian by convention)."""
        return "little"
