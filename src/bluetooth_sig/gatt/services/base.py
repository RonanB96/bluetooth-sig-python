"""Base class for GATT service implementations."""

from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar, cast

import msgspec

from ...types import CharacteristicInfo as BaseCharacteristicInfo
from ...types import ServiceInfo
from ...types.gatt_services import (
    CharacteristicCollection,
    CharacteristicSpec,
    ServiceDiscoveryData,
)
from ...types.uuid import BluetoothUUID
from ..characteristics import BaseCharacteristic, CharacteristicRegistry
from ..characteristics.registry import CharacteristicName
from ..characteristics.unknown import UnknownCharacteristic
from ..exceptions import UUIDResolutionError
from ..resolver import ServiceRegistrySearch
from ..uuid_registry import UuidInfo, uuid_registry

# Type aliases
GattCharacteristic = BaseCharacteristic
# Strong-typed collection with enum keys
ServiceCharacteristicCollection = CharacteristicCollection  # Alias for compatibility

# Generic type variable for service-specific characteristic definitions
ServiceCharacteristics = TypeVar("ServiceCharacteristics")


# Internal collections are plain dicts keyed by `CharacteristicName` enums.
# Do not perform implicit string-based lookups here; callers must convert
# strings to `CharacteristicName` explicitly at public boundaries.


class ServiceValidationConfig(msgspec.Struct, kw_only=True):
    """Configuration for service validation constraints.

    Groups validation parameters into a single, optional configuration object
    to simplify BaseGattService constructor signatures.
    """

    strict_validation: bool = False
    require_all_optional: bool = False


class SIGServiceResolver:
    """Resolves SIG service information from registry.

    This class handles all SIG service resolution logic, separating
    concerns from the BaseGattService constructor. Uses shared utilities
    from the resolver module to avoid code duplication with characteristic resolution.
    """

    @staticmethod
    def resolve_for_class(service_class: type[BaseGattService]) -> ServiceInfo:
        """Resolve ServiceInfo for a SIG service class.

        Args:
            service_class: The service class to resolve info for

        Returns:
            ServiceInfo with resolved UUID, name, summary

        Raises:
            UUIDResolutionError: If no UUID can be resolved for the class

        """
        # Try configured info first (for custom services)
        if hasattr(service_class, "_info") and service_class._info is not None:
            return service_class._info

        # Try registry resolution
        registry_info = SIGServiceResolver.resolve_from_registry(service_class)
        if registry_info:
            return registry_info

        # No resolution found
        raise UUIDResolutionError(service_class.__name__, [service_class.__name__])

    @staticmethod
    def resolve_from_registry(service_class: type[BaseGattService]) -> ServiceInfo | None:
        """Resolve service info from registry using shared search strategy."""
        # Use shared registry search strategy
        search_strategy = ServiceRegistrySearch()
        service_name = getattr(service_class, "_service_name", None)
        return search_strategy.search(service_class, service_name)


class ServiceHealthStatus(Enum):
    """Health status of a GATT service."""

    COMPLETE = "complete"  # All required characteristics present
    FUNCTIONAL = "functional"  # Required characteristics present, some optional missing
    PARTIAL = "partial"  # Some required characteristics missing but service still usable
    INCOMPLETE = "incomplete"  # Critical required characteristics missing


class CharacteristicStatus(Enum):
    """Status of characteristics within a service."""

    PRESENT = "present"  # Characteristic is present and functional
    MISSING = "missing"  # Expected characteristic not found
    INVALID = "invalid"  # Characteristic found but invalid/unusable


class ServiceValidationResult(msgspec.Struct, kw_only=True):
    """Result of service validation."""

    status: ServiceHealthStatus
    missing_required: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    missing_optional: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    invalid_characteristics: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    warnings: list[str] = msgspec.field(default_factory=list)
    errors: list[str] = msgspec.field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Check if service is in a healthy state."""
        return self.status in (
            ServiceHealthStatus.COMPLETE,
            ServiceHealthStatus.FUNCTIONAL,
        )

    @property
    def has_errors(self) -> bool:
        """Check if service has any errors."""
        return len(self.errors) > 0 or len(self.missing_required) > 0


class ServiceCharacteristicInfo(BaseCharacteristicInfo):
    """Service-specific information about a characteristic with context about its presence.

    Provides status, requirement, and class context for a characteristic within a service.
    """

    status: CharacteristicStatus = CharacteristicStatus.INVALID
    is_required: bool = False
    is_conditional: bool = False
    condition_description: str = ""
    char_class: type[BaseCharacteristic] | None = None


class ServiceCompletenessReport(msgspec.Struct, kw_only=True):  # pylint: disable=too-many-instance-attributes
    """Comprehensive report about service completeness and health."""

    service_name: str
    service_uuid: BluetoothUUID
    health_status: ServiceHealthStatus
    is_healthy: bool
    characteristics_present: int
    characteristics_expected: int
    characteristics_required: int
    present_characteristics: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    missing_required: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    missing_optional: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    invalid_characteristics: list[BaseCharacteristic] = msgspec.field(default_factory=list)
    warnings: list[str] = msgspec.field(default_factory=list)
    errors: list[str] = msgspec.field(default_factory=list)
    missing_details: dict[str, ServiceCharacteristicInfo] = msgspec.field(default_factory=dict)


# All type definitions moved to src/bluetooth_sig/types/gatt_services.py
# Import them at the top of this file when needed


class BaseGattService:  # pylint: disable=too-many-public-methods
    """Base class for all GATT services.

    Automatically resolves UUID, name, and summary from Bluetooth SIG specifications.
    Follows the same pattern as BaseCharacteristic for consistency.
    """

    # Class attributes for explicit name overrides
    _service_name: str | None = None
    _info: ServiceInfo | None = None  # Populated in __post_init__

    def __init__(
        self,
        info: ServiceInfo | None = None,
        validation: ServiceValidationConfig | None = None,
    ) -> None:
        """Initialize service with structured configuration.

        Args:
            info: Complete service information (optional for SIG services)
            validation: Validation constraints configuration (optional)

        """
        # Store provided info or None (will be resolved in __post_init__)
        self._provided_info = info

        self.characteristics: dict[BluetoothUUID, BaseCharacteristic] = {}

        # Set validation attributes from ServiceValidationConfig
        if validation:
            self.strict_validation = validation.strict_validation
            self.require_all_optional = validation.require_all_optional
        else:
            self.strict_validation = False
            self.require_all_optional = False

        # Call post-init to resolve service info
        self.__post_init__()

    def __post_init__(self) -> None:
        """Initialize service with resolved information."""
        # Use provided info if available, otherwise resolve from SIG specs
        if self._provided_info:
            self._info = self._provided_info
        else:
            # Resolve service information using proper resolver
            self._info = SIGServiceResolver.resolve_for_class(type(self))

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the service UUID from _info."""
        assert self._info is not None, "Service info should be initialized in __post_init__"
        return self._info.uuid

    @property
    def name(self) -> str:
        """Get the service name from _info."""
        assert self._info is not None, "Service info should be initialized in __post_init__"
        return self._info.name

    @property
    def summary(self) -> str:
        """Get the service summary from _info."""
        assert self._info is not None, "Service info should be initialized in __post_init__"
        return self._info.description

    @property
    def info(self) -> ServiceInfo:
        """Return the resolved service information for this instance.

        The info property provides all metadata about the service, including UUID, name, and description.
        """
        assert self._info is not None, "Service info should be initialized in __post_init__"
        return self._info

    @classmethod
    def get_class_uuid(cls) -> BluetoothUUID:
        """Get the UUID for this service class without instantiation.

        Returns:
            BluetoothUUID for this service class

        Raises:
            UUIDResolutionError: If UUID cannot be resolved

        """
        info = SIGServiceResolver.resolve_for_class(cls)
        return info.uuid

    @classmethod
    def get_name(cls) -> str:
        """Get the service name for this class without creating an instance.

        Returns:
            The service name as registered in the UUID registry.

        """
        # Try configured info first (for custom services)
        if hasattr(cls, "_info") and cls._info is not None:
            return cls._info.name

        # For SIG services, resolve from registry
        uuid = cls.get_class_uuid()
        service_info = uuid_registry.get_service_info(uuid)
        if service_info:
            return service_info.name

        # Fallback to class name
        return cls.__name__

    @classmethod
    def matches_uuid(cls, uuid: str | BluetoothUUID) -> bool:
        """Check if this service matches the given UUID."""
        try:
            service_uuid = cls.get_class_uuid()
            if isinstance(uuid, BluetoothUUID):
                input_uuid = uuid
            else:
                input_uuid = BluetoothUUID(uuid)
            return service_uuid == input_uuid
        except (ValueError, UUIDResolutionError):
            return False

    @classmethod
    def get_expected_characteristics(cls) -> ServiceCharacteristicCollection:
        """Get the expected characteristics for this service from the service_characteristics dict.

        Looks for a 'service_characteristics' class attribute containing a dictionary of
            CharacteristicName -> required flag, and automatically builds CharacteristicSpec objects.

        Returns:
            ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

        """
        # Build expected mapping keyed by CharacteristicName enum for type safety.
        expected: dict[CharacteristicName, CharacteristicSpec[BaseCharacteristic]] = {}

        # Check if the service defines a service_characteristics dictionary
        svc_chars = getattr(cls, "service_characteristics", None)
        if svc_chars:
            for char_name, is_required in svc_chars.items():
                char_class = CharacteristicRegistry.get_characteristic_class(char_name)
                if char_class:
                    expected[char_name] = CharacteristicSpec(char_class=char_class, required=is_required)

        # Return an enum-keyed dict for strong typing. Callers must perform
        # explicit conversions from strings to `CharacteristicName` where needed.
        return expected

    @classmethod
    def get_required_characteristics(cls) -> ServiceCharacteristicCollection:
        """Get the required characteristics for this service from the characteristics dict.

        Automatically filters the characteristics dictionary for required=True entries.

        Returns:
            ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

        """
        expected = cls.get_expected_characteristics()
        return {name: spec for name, spec in expected.items() if spec.required}

    # New strongly-typed methods (optional to implement)
    @classmethod
    def get_characteristics_schema(cls) -> type | None:
        """Get the TypedDict schema for this service's characteristics.

        Override this method to provide strong typing for characteristics.
        If not implemented, falls back to get_expected_characteristics().

        Returns:
            TypedDict class defining the service's characteristics, or None

        """
        return None

    @classmethod
    def get_required_characteristic_keys(cls) -> set[CharacteristicName]:
        """Get the set of required characteristic keys from the schema.

        Override this method when using strongly-typed characteristics.
        If not implemented, falls back to get_required_characteristics().keys().

        Returns:
            Set of required characteristic field names

        """
        return set(cls.get_required_characteristics().keys())

    def get_expected_characteristic_uuids(self) -> set[BluetoothUUID]:
        """Get the set of expected characteristic UUIDs for this service."""
        expected_uuids: set[BluetoothUUID] = set()
        for char_name, _char_spec in self.get_expected_characteristics().items():
            # char_name is expected to be a CharacteristicName enum; handle accordingly
            try:
                lookup_name = char_name.value
            except AttributeError:
                lookup_name = str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)
            if char_info:
                expected_uuids.add(char_info.uuid)
        return expected_uuids

    def get_required_characteristic_uuids(self) -> set[BluetoothUUID]:
        """Get the set of required characteristic UUIDs for this service."""
        required_uuids: set[BluetoothUUID] = set()
        for char_name, _char_spec in self.get_required_characteristics().items():
            try:
                lookup_name = char_name.value
            except AttributeError:
                lookup_name = str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)
            if char_info:
                required_uuids.add(char_info.uuid)
        return required_uuids

    def process_characteristics(self, characteristics: ServiceDiscoveryData) -> None:
        """Process the characteristics for this service (default implementation).

        Args:
            characteristics: Dict mapping UUID to characteristic info

        """
        for uuid_obj, char_info in characteristics.items():
            char_instance = CharacteristicRegistry.create_characteristic(uuid=uuid_obj.normalized)

            if char_instance is None:
                # Create UnknownCharacteristic for unregistered characteristics
                char_instance = UnknownCharacteristic(
                    info=BaseCharacteristicInfo(
                        uuid=uuid_obj,
                        name=char_info.name or f"Unknown Characteristic ({uuid_obj})",
                        unit=char_info.unit or "",
                        value_type=char_info.value_type,
                    ),
                    properties=[],
                )

            self.characteristics[uuid_obj] = char_instance

    def get_characteristic(self, uuid: BluetoothUUID) -> GattCharacteristic | None:
        """Get a characteristic by UUID."""
        if isinstance(uuid, str):
            uuid = BluetoothUUID(uuid)
        return self.characteristics.get(uuid)

    @property
    def supported_characteristics(self) -> set[BaseCharacteristic]:
        """Get the set of characteristic UUIDs supported by this service."""
        # Return set of characteristic instances, not UUID strings
        return set(self.characteristics.values())

    @classmethod
    def get_optional_characteristics(cls) -> ServiceCharacteristicCollection:
        """Get the optional characteristics for this service by name and class.

        Returns:
            ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

        """
        expected = cls.get_expected_characteristics()
        required = cls.get_required_characteristics()
        return {name: char_spec for name, char_spec in expected.items() if name not in required}

    @classmethod
    def get_conditional_characteristics(cls) -> ServiceCharacteristicCollection:
        """Get characteristics that are required only under certain conditions.

        Returns:
            ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

        Override in subclasses to specify conditional characteristics.

        """
        return {}

    @classmethod
    def validate_bluetooth_sig_compliance(cls) -> list[str]:
        """Validate compliance with Bluetooth SIG service specification.

        Returns:
            List of compliance issues found

        Override in subclasses to provide service-specific validation.

        """
        issues: list[str] = []

        # Check if service has at least one required characteristic
        required = cls.get_required_characteristics()
        if not required:
            issues.append("Service has no required characteristics defined")

        # Check if all expected characteristics are valid
        expected = cls.get_expected_characteristics()
        for char_name, _char_spec in expected.items():
            char_info = uuid_registry.get_characteristic_info(char_name.value)
            if not char_info:
                issues.append(f"Characteristic '{char_name.value}' not found in UUID registry")

        return issues

    def _validate_characteristic_group(
        self,
        char_dict: ServiceCharacteristicCollection,
        result: ServiceValidationResult,
        is_required: bool,
        strict: bool,
    ) -> None:
        """Validate a group of characteristics (required/optional/conditional)."""
        for char_name, char_spec in char_dict.items():
            lookup_name = char_name.value if hasattr(char_name, "value") else str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)

            if not char_info:
                if is_required:
                    result.errors.append(f"Unknown required characteristic: {lookup_name}")
                elif strict:
                    result.warnings.append(f"Unknown optional characteristic: {lookup_name}")
                continue

            if char_info.uuid not in self.characteristics:
                missing_char = char_spec.char_class()
                if is_required:
                    result.missing_required.append(missing_char)
                    result.errors.append(f"Missing required characteristic: {lookup_name}")
                else:
                    result.missing_optional.append(missing_char)
                    if strict:
                        result.warnings.append(f"Missing optional characteristic: {lookup_name}")

    def _validate_conditional_characteristics(
        self, conditional_chars: ServiceCharacteristicCollection, result: ServiceValidationResult
    ) -> None:
        """Validate conditional characteristics."""
        for char_name, conditional_spec in conditional_chars.items():
            lookup_name = char_name.value if hasattr(char_name, "value") else str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)

            if not char_info:
                result.warnings.append(f"Unknown conditional characteristic: {lookup_name}")
                continue

            if char_info.uuid not in self.characteristics:
                result.warnings.append(
                    f"Missing conditional characteristic: {lookup_name} (required when {conditional_spec.condition})"
                )

    def _determine_health_status(self, result: ServiceValidationResult, required_count: int, strict: bool) -> None:
        """Determine overall service health status."""
        if result.missing_required:
            result.status = (
                ServiceHealthStatus.INCOMPLETE
                if len(result.missing_required) >= required_count
                else ServiceHealthStatus.PARTIAL
            )
        elif result.missing_optional and strict:
            result.status = ServiceHealthStatus.FUNCTIONAL
        elif result.warnings or result.invalid_characteristics:
            result.status = ServiceHealthStatus.FUNCTIONAL

    def validate_service(self, strict: bool = False) -> ServiceValidationResult:  # pylint: disable=too-many-branches
        """Validate the completeness and health of this service.

        Args:
            strict: If True, missing optional characteristics are treated as warnings

        Returns:
            ServiceValidationResult with detailed status information

        """
        result = ServiceValidationResult(status=ServiceHealthStatus.COMPLETE)

        # Validate required, optional, and conditional characteristics
        self._validate_characteristic_group(self.get_required_characteristics(), result, True, strict)
        self._validate_characteristic_group(self.get_optional_characteristics(), result, False, strict)
        self._validate_conditional_characteristics(self.get_conditional_characteristics(), result)

        # Validate existing characteristics
        for uuid, characteristic in self.characteristics.items():
            try:
                _ = characteristic.uuid
            except (AttributeError, ValueError, TypeError) as e:
                result.invalid_characteristics.append(characteristic)
                result.errors.append(f"Invalid characteristic {uuid}: {e}")

        # Determine overall health status
        self._determine_health_status(result, len(self.get_required_characteristics()), strict)

        return result

    def get_missing_characteristics(
        self,
    ) -> dict[CharacteristicName, ServiceCharacteristicInfo]:
        """Get detailed information about missing characteristics.

        Returns:
            Dict mapping characteristic name to ServiceCharacteristicInfo

        """
        missing: dict[CharacteristicName, ServiceCharacteristicInfo] = {}
        expected_chars = self.get_expected_characteristics()
        required_chars = self.get_required_characteristics()
        conditional_chars = self.get_conditional_characteristics()

        for char_name, _char_spec in expected_chars.items():
            char_info = uuid_registry.get_characteristic_info(char_name.value)
            if not char_info:
                continue

            uuid_obj = char_info.uuid
            if uuid_obj not in self.characteristics:
                is_required = char_name in required_chars
                is_conditional = char_name in conditional_chars
                condition_desc = ""
                if is_conditional:
                    conditional_spec = conditional_chars.get(char_name)
                    if conditional_spec:
                        condition_desc = conditional_spec.condition

                # Handle both new CharacteristicSpec format and legacy direct class format
                char_class = None
                if hasattr(_char_spec, "char_class"):
                    char_class = _char_spec.char_class  # New format
                else:
                    char_class = cast(
                        type[BaseCharacteristic], _char_spec
                    )  # Legacy format: value is the class directly

                missing[char_name] = ServiceCharacteristicInfo(
                    name=char_name.value,
                    uuid=char_info.uuid,
                    status=CharacteristicStatus.MISSING,
                    is_required=is_required,
                    is_conditional=is_conditional,
                    condition_description=condition_desc,
                    char_class=char_class,
                )

        return missing

    def _find_characteristic_enum(
        self, characteristic_name: str, expected_chars: dict[CharacteristicName, Any]
    ) -> CharacteristicName | None:
        """Find the enum that matches the characteristic name string.

        NOTE: This is an internal helper. Public APIs should accept
        `CharacteristicName` enums directly; this helper will only be used
        temporarily by migrating call sites.
        """
        for enum_char in expected_chars.keys():
            if enum_char.value == characteristic_name:
                return enum_char
        return None

    def _get_characteristic_metadata(self, char_enum: CharacteristicName) -> tuple[bool, bool, str]:
        """Get characteristic metadata (is_required, is_conditional, condition_desc).

        Returns metadata about the characteristic's requirement and condition.
        """
        required_chars = self.get_required_characteristics()
        conditional_chars = self.get_conditional_characteristics()

        is_required = char_enum in required_chars
        is_conditional = char_enum in conditional_chars
        condition_desc = ""
        if is_conditional:
            conditional_spec = conditional_chars.get(char_enum)
            if conditional_spec:
                condition_desc = conditional_spec.condition

        return is_required, is_conditional, condition_desc

    def _get_characteristic_status(self, char_info: UuidInfo) -> CharacteristicStatus:
        """Get the status of a characteristic (present, missing, or invalid).

        Returns the status of the characteristic for reporting and validation.
        """
        uuid_obj = char_info.uuid
        if uuid_obj in self.characteristics:
            try:
                # Try to validate the characteristic
                char = self.characteristics[uuid_obj]
                _ = char.uuid  # Basic validation
                return CharacteristicStatus.PRESENT
            except (KeyError, AttributeError, ValueError, TypeError):
                return CharacteristicStatus.INVALID
        return CharacteristicStatus.MISSING

    def get_characteristic_status(self, characteristic_name: CharacteristicName) -> ServiceCharacteristicInfo | None:
        """Get detailed status of a specific characteristic.

        Args:
            characteristic_name: CharacteristicName enum

        Returns:
            CharacteristicInfo if characteristic is expected by this service, None otherwise

        """
        expected_chars = self.get_expected_characteristics()

        char_enum = characteristic_name

        # Only return status for characteristics that are expected by this service
        if char_enum not in expected_chars:
            return None

        char_info = uuid_registry.get_characteristic_info(char_enum.value)
        if not char_info:
            return None

        is_required, is_conditional, condition_desc = self._get_characteristic_metadata(char_enum)

        char_class = None
        if char_enum in expected_chars:
            char_spec = expected_chars[char_enum]
            if hasattr(char_spec, "char_class"):
                char_class = char_spec.char_class  # New format
            else:
                char_class = cast(type[BaseCharacteristic], char_spec)  # Legacy format: value is the class directly

        status = self._get_characteristic_status(char_info)

        return ServiceCharacteristicInfo(
            name=characteristic_name.value,
            uuid=char_info.uuid,
            status=status,
            is_required=is_required,
            is_conditional=is_conditional,
            condition_description=condition_desc,
            char_class=char_class,
        )

    def get_service_completeness_report(self) -> ServiceCompletenessReport:
        """Get a comprehensive report about service completeness.

        Returns:
            ServiceCompletenessReport with detailed service status information

        """
        validation = self.validate_service(strict=True)
        missing = self.get_missing_characteristics()

        present_chars: list[str] = []
        for uuid, char in self.characteristics.items():
            try:
                char_name = char.name if hasattr(char, "name") else f"UUID:{str(uuid)}"
                present_chars.append(char_name)
            except (AttributeError, ValueError, TypeError):
                present_chars.append(f"Invalid:{str(uuid)}")

        missing_details = {
            name.value: ServiceCharacteristicInfo(
                name=info.name,
                uuid=info.uuid,
                status=info.status,
                is_required=info.is_required,
                is_conditional=info.is_conditional,
                condition_description=info.condition_description,
            )
            for name, info in missing.items()
        }

        return ServiceCompletenessReport(
            service_name=self.name,
            service_uuid=self.uuid,
            health_status=validation.status,
            is_healthy=validation.is_healthy,
            characteristics_present=len(self.characteristics),
            characteristics_expected=len(self.get_expected_characteristics()),
            characteristics_required=len(self.get_required_characteristics()),
            present_characteristics=list(self.characteristics.values()),
            missing_required=validation.missing_required,
            missing_optional=validation.missing_optional,
            invalid_characteristics=validation.invalid_characteristics,
            warnings=validation.warnings,
            errors=validation.errors,
            missing_details=missing_details,
        )

    def has_minimum_functionality(self) -> bool:
        """Check if service has minimum required functionality.

        Returns:
            True if service has all required characteristics and is usable

        """
        validation = self.validate_service()
        return (not validation.missing_required) and (validation.status != ServiceHealthStatus.INCOMPLETE)
