"""Base class for GATT service implementations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeVar, cast

from ...types import CharacteristicInfo as BaseCharacteristicInfo
from ...types.gatt_enums import GattProperty
from ...types.gatt_services import (
    CharacteristicCollection,
    CharacteristicSpec,
    ServiceDiscoveryData,
)
from ..characteristics import BaseCharacteristic, CharacteristicRegistry
from ..characteristics.registry import CharacteristicName
from ..exceptions import UUIDResolutionError
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


@dataclass
class ServiceValidationResult:
    """Result of service validation."""

    status: ServiceHealthStatus
    missing_required: list[str] = field(default_factory=lambda: cast(list[str], []))
    missing_optional: list[str] = field(default_factory=lambda: cast(list[str], []))
    invalid_characteristics: list[str] = field(default_factory=lambda: cast(list[str], []))
    warnings: list[str] = field(default_factory=lambda: cast(list[str], []))
    errors: list[str] = field(default_factory=lambda: cast(list[str], []))

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


@dataclass
class ServiceCharacteristicInfo(BaseCharacteristicInfo):
    """Service-specific information about a characteristic with context about
    its presence."""

    status: CharacteristicStatus = CharacteristicStatus.PRESENT
    is_required: bool = False
    is_conditional: bool = False
    condition_description: str = ""
    char_class: type[BaseCharacteristic] | None = None


@dataclass
class ServiceCompletenessReport:  # pylint: disable=too-many-instance-attributes
    """Comprehensive report about service completeness and health."""

    service_name: str
    service_uuid: str
    health_status: str
    is_healthy: bool
    characteristics_present: int
    characteristics_expected: int
    characteristics_required: int
    present_characteristics: list[str] = field(default_factory=lambda: [])
    missing_required: list[str] = field(default_factory=lambda: [])
    missing_optional: list[str] = field(default_factory=lambda: [])
    invalid_characteristics: list[str] = field(default_factory=lambda: [])
    warnings: list[str] = field(default_factory=lambda: [])
    errors: list[str] = field(default_factory=lambda: [])
    missing_details: dict[str, ServiceCharacteristicInfo] = field(default_factory=lambda: {})


# All type definitions moved to src/bluetooth_sig/types/gatt_services.py
# Import them at the top of this file when needed


@dataclass
class BaseGattService:  # pylint: disable=too-many-public-methods
    """Base class for all GATT services."""

    # Instance variables
    characteristics: dict[str, BaseCharacteristic] = field(
        default_factory=lambda: cast(dict[str, BaseCharacteristic], {})
    )
    _service_name: str = ""  # Override in subclasses with service name string

    @property
    def SERVICE_UUID(self) -> str:
        """Get the service UUID from registry based on class name."""
        # First try explicit service name if set
        if hasattr(self, "_service_name") and self._service_name:
            info = uuid_registry.get_service_info(self._service_name)
            if info:
                return info.uuid

        # Convert class name to standard format and try all possibilities
        name = self.__class__.__name__

        # Try different name formats:
        # 1. Full class name (e.g., BatteryService)
        # 2. Without 'Service' suffix (e.g., Battery)
        # 3. As standard service ID
        # (e.g., org.bluetooth.service.battery_service)
        # Format name for lookup
        service_name = name
        if name.endswith("Service"):
            service_name = name[:-7]  # Remove 'Service' suffix

        # Split on camelCase and convert to space-separated
        words = re.findall("[A-Z][^A-Z]*", service_name)
        display_name = " ".join(words)

        # Try different name formats
        names_to_try = [
            name,  # Full class name (e.g. BatteryService)
            service_name,  # Without 'Service' suffix
            display_name,  # Space-separated (e.g. Environmental Sensing)
            display_name + " Service",  # With Service suffix
            # Service-specific format
            "org.bluetooth.service." + "_".join(words).lower(),
        ]

        # Try each name format
        for try_name in names_to_try:
            info = uuid_registry.get_service_info(try_name)
            if info:
                return info.uuid

        raise UUIDResolutionError(name, names_to_try)

    @property
    def name(self) -> str:
        """Get the service name from UUID registry."""
        info = uuid_registry.get_service_info(self.SERVICE_UUID)
        return info.name if info else f"Unknown Service ({self.SERVICE_UUID})"

    @property
    def summary(self) -> str:
        """Get the service summary."""
        info = uuid_registry.get_service_info(self.SERVICE_UUID)
        return info.summary if info else ""

    @classmethod
    def matches_uuid(cls, uuid: str) -> bool:
        """Check if this service matches the given UUID."""
        try:
            service_uuid = cls().SERVICE_UUID.lower()
            input_uuid = uuid.lower().replace("-", "")

            # If service UUID is short (16-bit), convert to full format for comparison
            if len(service_uuid) == 4:  # 16-bit UUID
                service_uuid = f"0000{service_uuid}00001000800000805f9b34fb"

            # If input UUID is short (16-bit), convert to full format for comparison
            if len(input_uuid) == 4:  # 16-bit UUID
                input_uuid = f"0000{input_uuid}00001000800000805f9b34fb"

            return service_uuid == input_uuid
        except ValueError:
            return False

    @classmethod
    def get_expected_characteristics(cls) -> ServiceCharacteristicCollection:
        """Get the expected characteristics for this service from the
        service_characteristics dict.

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
        """Get the required characteristics for this service from the
        characteristics dict.

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
    def get_required_characteristic_keys(cls) -> set[str]:
        """Get the set of required characteristic keys from the schema.

        Override this method when using strongly-typed characteristics.
        If not implemented, falls back to get_required_characteristics().keys().

        Returns:
            Set of required characteristic field names
        """
        return set()

    def get_expected_characteristic_uuids(self) -> set[str]:
        """Get the set of expected characteristic UUIDs for this service."""
        expected_uuids: set[str] = set()
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

    def get_required_characteristic_uuids(self) -> set[str]:
        """Get the set of required characteristic UUIDs for this service."""
        required_uuids: set[str] = set()
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
        """Process the characteristics for this service (default
        implementation).

        Args:
            characteristics: Dict mapping UUID to characteristic properties
        """
        for uuid, props in characteristics.items():
            uuid = uuid.replace("-", "").upper()
            prop_vals = set(props.get("properties", []))
            char = CharacteristicRegistry.create_characteristic(
                uuid_or_name=uuid,
                properties=cast(Optional[set[GattProperty]], prop_vals),
            )
            if char:
                self.characteristics[uuid] = char

    def get_characteristic(self, uuid: str) -> GattCharacteristic | None:
        """Get a characteristic by UUID."""
        return self.characteristics.get(uuid.lower())

    @property
    def supported_characteristics(self) -> set[str]:
        """Get the set of characteristic UUIDs supported by this service."""
        return set(self.characteristics.keys())

    # New enhanced methods for service validation and health

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

    def validate_service(self, strict: bool = False) -> ServiceValidationResult:  # pylint: disable=too-many-branches,R0915
        """Validate the completeness and health of this service.

        Args:
            strict: If True, missing optional characteristics are treated as warnings

        Returns:
            ServiceValidationResult with detailed status information
        """
        result = ServiceValidationResult(status=ServiceHealthStatus.COMPLETE)

        required_chars = self.get_required_characteristics()
        optional_chars = self.get_optional_characteristics()
        conditional_chars = self.get_conditional_characteristics()

        # Check required characteristics
        for char_name, _char_spec in required_chars.items():
            try:
                lookup_name = char_name.value
            except AttributeError:
                lookup_name = str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)
            if not char_info:
                result.errors.append(f"Unknown required characteristic: {lookup_name}")
                continue

            if char_info.uuid not in self.characteristics:
                result.missing_required.append(lookup_name)
                result.errors.append(f"Missing required characteristic: {lookup_name}")

        # Check optional characteristics
        for char_name, _char_spec in optional_chars.items():
            try:
                lookup_name = char_name.value
            except AttributeError:
                lookup_name = str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)
            if not char_info:
                if strict:
                    result.warnings.append(f"Unknown optional characteristic: {lookup_name}")
                continue

            if char_info.uuid not in self.characteristics:
                result.missing_optional.append(lookup_name)
                if strict:
                    result.warnings.append(f"Missing optional characteristic: {lookup_name}")

        # Check conditional characteristics
        for char_name, conditional_spec in conditional_chars.items():
            try:
                lookup_name = char_name.value
            except AttributeError:
                lookup_name = str(char_name)
            char_info = uuid_registry.get_characteristic_info(lookup_name)
            if not char_info:
                result.warnings.append(f"Unknown conditional characteristic: {lookup_name}")
                continue

            # For now, just report missing conditional characteristics as warnings
            if char_info.uuid not in self.characteristics:
                condition = conditional_spec.condition
                result.warnings.append(f"Missing conditional characteristic: {lookup_name} (required when {condition})")

        # Validate existing characteristics
        for uuid, characteristic in self.characteristics.items():
            try:
                # Basic validation - check if characteristic can provide its UUID
                _ = characteristic.char_uuid
            except (AttributeError, ValueError, TypeError) as e:
                result.invalid_characteristics.append(uuid)
                result.errors.append(f"Invalid characteristic {uuid}: {e}")

        # Determine overall service health status
        if result.missing_required:
            if len(result.missing_required) >= len(required_chars):
                result.status = ServiceHealthStatus.INCOMPLETE
            else:
                result.status = ServiceHealthStatus.PARTIAL
        elif result.missing_optional and strict:
            result.status = ServiceHealthStatus.FUNCTIONAL
        elif result.warnings or result.invalid_characteristics:
            result.status = ServiceHealthStatus.FUNCTIONAL
        else:
            result.status = ServiceHealthStatus.COMPLETE

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

            if char_info.uuid not in self.characteristics:
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
        """Get characteristic metadata (is_required, is_conditional,
        condition_desc)."""
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
        """Get the status of a characteristic (present, missing, or
        invalid)."""
        if char_info.uuid in self.characteristics:
            try:
                # Try to validate the characteristic
                char = self.characteristics[char_info.uuid]
                _ = char.char_uuid  # Basic validation
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
                char_name = char.name if hasattr(char, "name") else f"UUID:{uuid}"
                present_chars.append(char_name)
            except (AttributeError, ValueError, TypeError):
                present_chars.append(f"Invalid:{uuid}")

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
            service_uuid=self.SERVICE_UUID,
            health_status=validation.status.value,
            is_healthy=validation.is_healthy,
            characteristics_present=len(self.characteristics),
            characteristics_expected=len(self.get_expected_characteristics()),
            characteristics_required=len(self.get_required_characteristics()),
            present_characteristics=sorted(present_chars),
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
