"""GATT exceptions for the Bluetooth SIG library."""

from __future__ import annotations

from typing import Any

from ..types import ParseFieldError as FieldError
from ..types import SpecialValueResult
from ..types.data_types import ValidationAccumulator
from ..types.uuid import BluetoothUUID


class BluetoothSIGError(Exception):
    """Base exception for all Bluetooth SIG related errors."""


class CharacteristicError(BluetoothSIGError):
    """Base exception for characteristic-related errors."""


class ServiceError(BluetoothSIGError):
    """Base exception for service-related errors."""


class UUIDResolutionError(BluetoothSIGError):
    """Exception raised when UUID resolution fails."""

    def __init__(self, name: str, attempted_names: list[str] | None = None) -> None:
        """Initialise UUIDResolutionError.

        Args:
            name: The name for which UUID resolution failed.
            attempted_names: List of attempted names.

        """
        self.name = name
        self.attempted_names = attempted_names or []
        message = f"No UUID found for: {name}"
        if self.attempted_names:
            message += f". Tried: {', '.join(self.attempted_names)}"
        super().__init__(message)


class DataParsingError(CharacteristicError):
    """Exception raised when characteristic data parsing fails."""

    def __init__(self, characteristic: str, data: bytes | bytearray, reason: str) -> None:
        """Initialise DataParsingError.

        Args:
            characteristic: The characteristic name.
            data: The raw data that failed to parse.
            reason: Reason for the parsing failure.

        """
        self.characteristic = characteristic
        self.data = data
        self.reason = reason
        hex_data = " ".join(f"{byte:02X}" for byte in data)
        message = f"Failed to parse {characteristic} data [{hex_data}]: {reason}"
        super().__init__(message)


class ParseFieldError(DataParsingError):
    """Exception raised when a specific field fails to parse.

    This exception provides detailed context about which field failed, where it
    failed in the data, and why it failed. This enables actionable error messages
    and structured error reporting.

    NOTE: This exception intentionally has more arguments than the standard limit
    to provide complete field-level diagnostic information. The additional parameters
    (field, offset) are essential for actionable error messages and field-level debugging.

    Attributes:
        field: Name of the field that failed (e.g., "temperature", "flags")
        offset: Byte offset where the field starts in the raw data
        expected: Description of what was expected
        actual: Description of what was actually encountered

    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # NOTE: More arguments than standard limit required for complete field-level diagnostics
    def __init__(
        self,
        characteristic: str,
        field: str,
        data: bytes | bytearray,
        reason: str,
        offset: int | None = None,
    ) -> None:
        """Initialise ParseFieldError.

        Args:
            characteristic: The characteristic name.
            field: The field name.
            data: The raw data.
            reason: Reason for the parsing failure.
            offset: Optional offset in the data.

        """
        self.field = field
        self.offset = offset
        # Store the original reason before formatting
        self.field_reason = reason

        # Format message with field and offset information
        field_info = f"field '{field}'"
        if offset is not None:
            field_info = f"{field_info} at offset {offset}"

        detailed_reason = f"{field_info}: {reason}"
        super().__init__(characteristic, data, detailed_reason)


class DataEncodingError(CharacteristicError):
    """Exception raised when characteristic data encoding fails."""

    def __init__(self, characteristic: str, value: Any, reason: str) -> None:  # noqa: ANN401  # Reports errors for any value type
        """Initialise DataEncodingError.

        Args:
            characteristic: The characteristic name.
            value: The value that failed to encode.
            reason: Reason for the encoding failure.

        """
        self.characteristic = characteristic
        self.value = value
        self.reason = reason
        message = f"Failed to encode {characteristic} value {value}: {reason}"
        super().__init__(message)


class DataValidationError(CharacteristicError):
    """Exception raised when characteristic data validation fails."""

    def __init__(self, field: str, value: Any, expected: str) -> None:  # noqa: ANN401  # Validates any value type
        """Initialise DataValidationError.

        Args:
            field: The field name.
            value: The value that failed validation.
            expected: Expected value or description.

        """
        self.field = field
        self.value = value
        self.expected = expected
        message = f"Invalid {field}: {value} (expected {expected})"
        super().__init__(message)


class InsufficientDataError(DataParsingError):
    """Exception raised when there is insufficient data for parsing."""

    def __init__(self, characteristic: str, data: bytes | bytearray, required: int) -> None:
        """Initialise InsufficientDataError.

        Args:
            characteristic: The characteristic name.
            data: The raw data.
            required: Required length of data.

        """
        self.required = required
        self.actual = len(data)
        reason = f"need {required} bytes, got {self.actual}"
        super().__init__(characteristic, data, reason)


class ValueRangeError(DataValidationError):
    """Exception raised when a value is outside the expected range."""

    def __init__(self, field: str, value: Any, min_val: Any, max_val: Any) -> None:  # noqa: ANN401  # Validates ranges for various numeric types
        """Initialise RangeValidationError.

        Args:
            field: The field name.
            value: The value to validate.
            min_val: Minimum valid value.
            max_val: Maximum valid value.

        """
        self.min_val = min_val
        self.max_val = max_val
        expected = f"range [{min_val}, {max_val}]"
        super().__init__(field, value, expected)


class TypeMismatchError(DataValidationError):
    """Exception raised when a value has an unexpected type."""

    expected_type: type | tuple[type, ...]
    actual_type: type

    def __init__(self, field: str, value: Any, expected_type: type | tuple[type, ...]) -> None:  # noqa: ANN401  # Reports type errors for any value
        """Initialise TypeValidationError.

        Args:
            field: The field name.
            value: The value to validate.
            expected_type: Expected type(s).

        """
        self.expected_type = expected_type
        self.actual_type = type(value)

        # Handle tuple of types for display
        if isinstance(expected_type, tuple):
            type_names = " or ".join(t.__name__ for t in expected_type)
            expected = f"type {type_names}, got {self.actual_type.__name__}"
        else:
            expected = f"type {expected_type.__name__}, got {self.actual_type.__name__}"

        super().__init__(field, value, expected)


class MissingDependencyError(CharacteristicError):
    """Exception raised when a required dependency is missing for multi-characteristic parsing."""

    def __init__(self, characteristic: str, missing_dependencies: list[str]) -> None:
        """Initialise DependencyValidationError.

        Args:
            characteristic: The characteristic name.
            missing_dependencies: List of missing dependencies.

        """
        self.characteristic = characteristic
        self.missing_dependencies = missing_dependencies
        dep_list = ", ".join(missing_dependencies)
        message = f"{characteristic} requires missing dependencies: {dep_list}"
        super().__init__(message)


class EnumValueError(DataValidationError):
    """Exception raised when an enum value is invalid."""

    def __init__(self, field: str, value: Any, enum_class: type, valid_values: list[Any]) -> None:  # noqa: ANN401  # Validates enum values of any type
        """Initialise EnumValidationError.

        Args:
            field: The field name.
            value: The value to validate.
            enum_class: Enum class for validation.
            valid_values: List of valid values.

        """
        self.enum_class = enum_class
        self.valid_values = valid_values
        expected = f"{enum_class.__name__} value from {valid_values}"
        super().__init__(field, value, expected)


class IEEE11073Error(DataParsingError):
    """Exception raised when IEEE 11073 format parsing fails."""

    def __init__(self, data: bytes | bytearray, format_type: str, reason: str) -> None:
        """Initialise DataFormatError.

        Args:
            data: The raw data.
            format_type: Format type expected.
            reason: Reason for the format error.

        """
        self.format_type = format_type
        characteristic = f"IEEE 11073 {format_type}"
        super().__init__(characteristic, data, reason)


class YAMLResolutionError(BluetoothSIGError):
    """Exception raised when YAML specification resolution fails."""

    def __init__(self, name: str, yaml_type: str) -> None:
        """Initialise YAMLSchemaError.

        Args:
            name: Name of the YAML entity.
            yaml_type: Type of the YAML entity.

        """
        self.name = name
        self.yaml_type = yaml_type
        message = f"Failed to resolve {yaml_type} specification for: {name}"
        super().__init__(message)


class ServiceCharacteristicMismatchError(ServiceError):
    """Exception raised when expected characteristics are not found in a service.

    service.
    """

    def __init__(self, service: str, missing_characteristics: list[str]) -> None:
        """Initialise ExpectedCharacteristicNotFound.

        Args:
            service: The service name.
            missing_characteristics: List of missing characteristics.

        """
        self.service = service
        self.missing_characteristics = missing_characteristics
        message = f"Service {service} missing required characteristics: {', '.join(missing_characteristics)}"
        super().__init__(message)


class TemplateConfigurationError(CharacteristicError):
    """Exception raised when a template is incorrectly configured."""

    def __init__(self, template: str, configuration_issue: str) -> None:
        """Initialise TemplateConfigurationError.

        Args:
            template: The template name.
            configuration_issue: Description of the configuration issue.

        """
        self.template = template
        self.configuration_issue = configuration_issue
        message = f"Template {template} configuration error: {configuration_issue}"
        super().__init__(message)


class UUIDRequiredError(BluetoothSIGError):
    """Exception raised when a UUID is required but not provided or invalid."""

    def __init__(self, class_name: str, entity_type: str) -> None:
        """Initialise EntityRegistrationError.

        Args:
            class_name: Name of the class.
            entity_type: Type of the entity.

        """
        self.class_name = class_name
        self.entity_type = entity_type
        message = (
            f"Custom {entity_type} '{class_name}' requires a valid UUID. "
            f"Provide a non-empty UUID when instantiating custom {entity_type}s."
        )
        super().__init__(message)


class UUIDCollisionError(BluetoothSIGError):
    """Exception raised when attempting to use a UUID that already exists in SIG registry."""

    def __init__(self, uuid: BluetoothUUID | str, existing_name: str, class_name: str) -> None:
        """Initialise UUIDRegistrationError.

        Args:
            uuid: The UUID value.
            existing_name: Existing name for the UUID.
            class_name: Name of the class.

        """
        self.uuid = uuid
        self.existing_name = existing_name
        self.class_name = class_name
        message = (
            f"UUID '{uuid}' is already used by SIG characteristic '{existing_name}'. "
            f"Cannot create custom characteristic '{class_name}' with existing SIG UUID. "
            f"Use allow_sig_override=True if you intentionally want to override this SIG characteristic."
        )
        super().__init__(message)


class CharacteristicParseError(CharacteristicError):
    """Raised when characteristic parsing fails.

    Preserves all debugging context from parsing attempt.

    Attributes:
        message: Human-readable error message
        name: Characteristic name
        uuid: Characteristic UUID
        raw_data: Exact bytes that failed (useful: hex dump debugging)
        raw_int: Extracted integer value (useful: check bit patterns)
        field_errors: Field-level errors (useful: complex multi-field characteristics)
        parse_trace: Step-by-step execution log (useful: debug parser flow)
        validation: Accumulated validation results (useful: see all warnings/errors)

    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # NOTE: Multiple arguments required for complete diagnostic context
    def __init__(
        self,
        message: str,
        name: str,
        uuid: BluetoothUUID,
        raw_data: bytes,
        raw_int: int | None = None,
        field_errors: list[FieldError] | None = None,
        parse_trace: list[str] | None = None,
        validation: ValidationAccumulator | None = None,
    ) -> None:
        """Initialize parse error with diagnostic context.

        Args:
            message: Human-readable error message
            name: Characteristic name
            uuid: Characteristic UUID
            raw_data: Raw bytes that failed to parse
            raw_int: Extracted integer (if extraction succeeded)
            field_errors: Field-level parsing errors
            parse_trace: Step-by-step execution log
            validation: Accumulated validation results

        """
        super().__init__(message)
        self.name = name
        self.uuid = uuid
        self.raw_data = raw_data
        self.raw_int = raw_int
        self.field_errors = field_errors or []
        self.parse_trace = parse_trace or []
        self.validation = validation

    def __str__(self) -> str:
        """Format error with field-level details."""
        base = f"{self.name} ({self.uuid}): {self.args[0]}"
        if self.field_errors:
            field_msgs = [f"  - {e.field}: {e.reason}" for e in self.field_errors]
            return f"{base}\nField errors:\n" + "\n".join(field_msgs)
        return base


class SpecialValueDetectedError(CharacteristicError):
    """Raised when a special sentinel value is detected.

    Special values represent exceptional conditions: "value is not known", "NaN",
    "measurement not possible", etc. These are semantically distinct from parse failures.

    This exception is raised when a valid parse detects a special sentinel value
    (e.g., 0x8000 = "value is not known", 0x7FFFFFFF = "NaN"). The parsing succeeded,
    but the result indicates an exceptional state rather than a normal value.

    Most code should catch this separately from CharacteristicParseError to distinguish:
    - Parse failure (malformed data, wrong length, invalid format)
    - Special value detection (well-formed data indicating exceptional state)

    Attributes:
        special_value: The detected special value with meaning and raw bytes
        name: Characteristic name
        uuid: Characteristic UUID
        raw_data: Raw bytes containing the special value
        raw_int: The raw integer value (typically the sentinel value)

    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        special_value: SpecialValueResult,
        name: str,
        uuid: BluetoothUUID,
        raw_data: bytes,
        raw_int: int | None = None,
    ) -> None:
        """Initialize special value detected exception.

        Args:
            special_value: The detected SpecialValueResult
            name: Characteristic name
            uuid: Characteristic UUID
            raw_data: Raw bytes containing the special value
            raw_int: The raw integer value

        """
        message = f"{name} ({uuid}): Special value detected: {special_value.meaning}"
        super().__init__(message)
        self.special_value = special_value
        self.name = name
        self.uuid = uuid
        self.raw_data = raw_data
        self.raw_int = raw_int


class CharacteristicEncodeError(CharacteristicError):
    """Raised when characteristic encoding fails.

    Attributes:
        message: Human-readable error message
        name: Characteristic name
        uuid: Characteristic UUID
        value: The value that failed to encode
        validation: Accumulated validation results

    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        message: str,
        name: str,
        uuid: BluetoothUUID,
        value: Any,  # noqa: ANN401  # Any value type
        validation: ValidationAccumulator | None = None,
    ) -> None:
        """Initialize encode error.

        Args:
            message: Human-readable error message
            name: Characteristic name
            uuid: Characteristic UUID
            value: The value that failed to encode
            validation: Accumulated validation results

        """
        super().__init__(message)
        self.name = name
        self.uuid = uuid
        self.value = value
        self.validation = validation
