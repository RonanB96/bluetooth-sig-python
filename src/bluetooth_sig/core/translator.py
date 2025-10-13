"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from graphlib import TopologicalSorter
from typing import Any, cast

from ..gatt.characteristics import CharacteristicName, CharacteristicRegistry
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.context import CharacteristicContext
from ..gatt.exceptions import MissingDependencyError
from ..gatt.services import SERVICE_CLASS_MAP, GattServiceRegistry, ServiceName
from ..gatt.services.base import BaseGattService
from ..gatt.uuid_registry import CustomUuidEntry, uuid_registry
from ..types import (
    CharacteristicData,
    CharacteristicDataProtocol,
    CharacteristicInfo,
    CharacteristicRegistration,
    ServiceInfo,
    ServiceRegistration,
    SIGInfo,
    ValidationResult,
)
from ..types.gatt_enums import ValueType
from ..types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class BluetoothSIGTranslator:  # pylint: disable=too-many-public-methods
    """Pure Bluetooth SIG standards translator for characteristic and service
    interpretation.

    Note: This class intentionally has >20 public methods as it serves as the
    primary API surface for Bluetooth SIG standards translation, covering
    characteristic parsing, service discovery, UUID resolution, and registry
    management. The methods are organized by functionality and reducing them
    would harm API clarity.
    """

    def __init__(self) -> None:
        """Initialize the SIG translator."""
        self._services: dict[str, BaseGattService] = {}

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    def parse_characteristic(
        self,
        uuid: str,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
        properties: set[str] | None = None,  # pylint: disable=unused-argument
    ) -> CharacteristicData:
        """Parse a characteristic's raw data using SIG standards.

        Args:
            uuid: The characteristic UUID (with or without dashes)
            raw_data: Raw bytes from the characteristic
            ctx: Optional `CharacteristicContext` providing device-level info
                and previously-parsed characteristics to the parser.
            properties: Optional set of characteristic properties (unused, kept for protocol compatibility)

        Returns:
            CharacteristicData with parsed value and metadata
        """
        logger.debug("Parsing characteristic UUID=%s, data_len=%d", uuid, len(raw_data))

        # Create characteristic instance for parsing
        characteristic = CharacteristicRegistry.create_characteristic(uuid)

        if characteristic:
            logger.debug("Found parser for UUID=%s: %s", uuid, type(characteristic).__name__)
            # Use the parse_value method; pass context when provided.
            result = characteristic.parse_value(raw_data, ctx)

            # Attach context if available and result doesn't already have it
            if ctx is not None:
                result.source_context = ctx

            if result.parse_success:
                logger.debug("Successfully parsed %s: %s", result.name, result.value)
            else:
                logger.warning("Parse failed for %s: %s", result.name, result.error_message)

            return result

        # No parser found, return fallback result
        logger.info("No parser available for UUID=%s", uuid)
        fallback_info = CharacteristicInfo(
            uuid=BluetoothUUID(uuid),
            name="Unknown",
            description="",
            value_type=ValueType.UNKNOWN,
            unit="",
            properties=[],
        )
        return CharacteristicData(
            info=fallback_info,
            value=raw_data,
            raw_data=raw_data,
            parse_success=False,
            error_message="No parser available for this characteristic UUID",
        )

    def get_characteristic_info(self, uuid: str) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID.

        Args:
            uuid: The characteristic UUID

        Returns:
            CharacteristicInfo with metadata or None if not found
        """
        try:
            bt_uuid = BluetoothUUID(uuid)
        except ValueError:
            return None

        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
        if not char_class:
            return None

        # Create temporary instance to get metadata (no parameters needed for auto-resolution)
        try:
            temp_char = char_class()
            return temp_char.info
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_characteristic_uuid(self, name: CharacteristicName) -> str | None:
        """Get the UUID for a characteristic name enum.

        Args:
            name: CharacteristicName enum

        Returns:
            Characteristic UUID or None if not found
        """
        char_class = CharacteristicRegistry.get_characteristic_class(name)
        if char_class:
            try:
                temp_char = char_class()
                return str(temp_char.info.uuid)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        return None

    def get_service_uuid(self, name: str | ServiceName) -> str | None:
        """Get the UUID for a service name or enum.

        Args:
            name: Service name or enum

        Returns:
            Service UUID or None if not found
        """
        # Try to find the service by name - use direct map access
        if isinstance(name, ServiceName):
            service_class = SERVICE_CLASS_MAP.get(name)
        else:
            # For string names, find the matching enum member
            service_class = None
            for enum_member in ServiceName:
                if enum_member.value == name:
                    service_class = SERVICE_CLASS_MAP.get(enum_member)
                    break

        if service_class:
            try:
                temp_service = service_class()
                return str(temp_service.uuid)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        return None

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> CharacteristicInfo | None:
        """Get characteristic info by enum name.

        Args:
            name: CharacteristicName enum

        Returns:
            CharacteristicInfo if found, None otherwise
        """
        char_class = CharacteristicRegistry.get_characteristic_class(name)
        if char_class:
            return char_class.get_configured_info()
        return None

    def get_service_info_by_name(self, name: str) -> ServiceInfo | None:
        """Get service info by name instead of UUID.

        Args:
            name: Service name

        Returns:
            ServiceInfo if found, None otherwise
        """
        # Use UUID registry for name-based lookup
        try:
            uuid_info = uuid_registry.get_service_info(name)
            if uuid_info:
                return ServiceInfo(uuid=uuid_info.uuid, name=uuid_info.name, characteristics=[])
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        return None

    def get_service_info(self, uuid: str) -> ServiceInfo | None:
        """Get information about a service by UUID.

        Args:
            uuid: The service UUID

        Returns:
            ServiceInfo with metadata or None if not found
        """
        service_class = GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID(uuid))
        if not service_class:
            return None

        try:
            temp_service = service_class()
            # Convert characteristics dict to list of CharacteristicInfo
            char_infos: list[CharacteristicInfo] = []
            for _, char_instance in temp_service.characteristics.items():
                # Use public info property
                char_infos.append(char_instance.info)
            return ServiceInfo(
                uuid=temp_service.uuid,
                name=temp_service.name,
                characteristics=char_infos,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs
        """
        result: dict[str, str] = {}
        for name, char_class in CharacteristicRegistry.get_all_characteristics().items():
            # Try to get configured_info from class using public accessor
            configured_info = char_class.get_configured_info()
            if configured_info:
                # Convert CharacteristicName enum to string for dict key
                name_str = name.value if hasattr(name, "value") else str(name)
                result[name_str] = str(configured_info.uuid)
        return result

    def list_supported_services(self) -> dict[str, str]:
        """List all supported services with their names and UUIDs.

        Returns:
            Dictionary mapping service names to UUIDs
        """
        result: dict[str, str] = {}
        for service_class in GattServiceRegistry.get_all_services():
            try:
                temp_service = service_class()
                service_name = getattr(temp_service, "_service_name", service_class.__name__)
                result[service_name] = str(temp_service.uuid)
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def process_services(self, services: dict[str, dict[str, dict[str, Any]]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics
        """
        for uuid_str, service_data in services.items():
            uuid = BluetoothUUID(uuid_str)
            # Convert dict[str, dict] to ServiceDiscoveryData
            characteristics: dict[BluetoothUUID, CharacteristicInfo] = {}
            for char_uuid_str, char_data in service_data.get("characteristics", {}).items():
                char_uuid = BluetoothUUID(char_uuid_str)
                # Create CharacteristicInfo from dict
                vtype_raw = char_data.get("value_type", "bytes")
                if isinstance(vtype_raw, str):
                    value_type = ValueType(vtype_raw)
                elif isinstance(vtype_raw, ValueType):
                    value_type = vtype_raw
                else:
                    value_type = ValueType.BYTES
                characteristics[char_uuid] = CharacteristicInfo(
                    uuid=char_uuid,
                    name=char_data.get("name", ""),
                    unit=char_data.get("unit", ""),
                    value_type=value_type,
                    properties=char_data.get("properties", []),
                )
            service = GattServiceRegistry.create_service(uuid, characteristics)
            if service:
                self._services[str(uuid)] = service

    def get_service(self, uuid: str) -> BaseGattService | None:
        """Get a service instance by UUID.

        Args:
            uuid: The service UUID

        Returns:
            Service instance if found, None otherwise
        """
        return self._services.get(uuid)

    @property
    def discovered_services(self) -> list[BaseGattService]:
        """Get list of discovered service instances.

        Returns:
            List of discovered service instances
        """
        return list(self._services.values())

    def clear_services(self) -> None:
        """Clear all discovered services."""
        self._services.clear()

    def resolve_uuid(self, name: str) -> SIGInfo | None:
        """Resolve a characteristic or service name to its full info.

        Args:
            name: Characteristic or service name

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise
        """
        # Use the UUID registry for name-based lookups (string inputs).
        try:
            char_info = uuid_registry.get_characteristic_info(name)
            if char_info:
                # Build CharacteristicInfo from registry data
                value_type = ValueType.UNKNOWN
                if char_info.value_type:
                    try:
                        value_type = ValueType(char_info.value_type)
                    except (ValueError, KeyError):
                        value_type = ValueType.UNKNOWN
                return CharacteristicInfo(
                    uuid=char_info.uuid,
                    name=char_info.name,
                    value_type=value_type,
                    unit=char_info.unit or "",
                )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # Try service
        service_info = self.get_service_info_by_name(name)
        if service_info:
            return service_info

        return None

    def resolve_name(self, uuid: str) -> SIGInfo | None:
        """Resolve a UUID to its full SIG information.

        Args:
            uuid: UUID string (with or without dashes)

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise
        """
        # Try characteristic first
        char_info = self.get_characteristic_info(uuid)
        if char_info:
            return char_info

        # Try service
        service_info = self.get_service_info(uuid)
        if service_info:
            return service_info

        return None

    def parse_characteristics(
        self, char_data: dict[str, bytes], ctx: CharacteristicContext | None = None
    ) -> dict[str, CharacteristicData]:
        """Parse multiple characteristics at once with dependency-aware ordering.

        This method automatically handles multi-characteristic dependencies by parsing
        independent characteristics first, then parsing characteristics that depend on them.
        The parsing order is determined by the `required_dependencies` and `optional_dependencies`
        attributes declared on characteristic classes.

        Required dependencies MUST be present and successfully parsed; missing required
        dependencies result in parse failure with MissingDependencyError. Optional dependencies
        enrich parsing when available but are not mandatory.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional base `CharacteristicContext` used as the starting
                device-level context for each parsed characteristic.

        Returns:
            Dictionary mapping UUIDs to CharacteristicData results

        Raises:
            ValueError: If circular dependencies are detected
        """
        logger.debug("Batch parsing %d characteristics", len(char_data))
        base_ctx = ctx

        (
            uuid_to_char,
            uuid_to_required_deps,
            uuid_to_optional_deps,
        ) = self._prepare_characteristic_dependencies(char_data)

        sorted_uuids = self._resolve_dependency_order(char_data, uuid_to_required_deps, uuid_to_optional_deps)

        results: dict[str, CharacteristicData] = {}
        for uuid_str in sorted_uuids:
            raw_data = char_data[uuid_str]
            characteristic = uuid_to_char.get(uuid_str)

            missing_required = self._find_missing_required_dependencies(
                uuid_str,
                uuid_to_required_deps.get(uuid_str, []),
                results,
                base_ctx,
            )

            if missing_required:
                results[uuid_str] = self._build_missing_dependency_failure(
                    uuid_str,
                    raw_data,
                    characteristic,
                    missing_required,
                )
                continue

            self._log_optional_dependency_gaps(
                uuid_str,
                uuid_to_optional_deps.get(uuid_str, []),
                results,
                base_ctx,
            )

            parse_ctx = self._build_parse_context(base_ctx, results)
            results[uuid_str] = self.parse_characteristic(uuid_str, raw_data, ctx=parse_ctx)

        logger.debug("Batch parsing complete: %d results", len(results))
        return results

    def _prepare_characteristic_dependencies(
        self, char_data: Mapping[str, bytes]
    ) -> tuple[dict[str, BaseCharacteristic], dict[str, list[str]], dict[str, list[str]]]:
        """Instantiate characteristics once and collect declared dependencies."""

        uuid_to_char: dict[str, BaseCharacteristic] = {}
        uuid_to_required_deps: dict[str, list[str]] = {}
        uuid_to_optional_deps: dict[str, list[str]] = {}

        for uuid in char_data:
            characteristic = CharacteristicRegistry.create_characteristic(uuid)
            if characteristic is None:
                continue

            uuid_to_char[uuid] = characteristic

            required = characteristic.required_dependencies
            optional = characteristic.optional_dependencies

            if required:
                uuid_to_required_deps[uuid] = required
                logger.debug("Characteristic %s has required dependencies: %s", uuid, required)
            if optional:
                uuid_to_optional_deps[uuid] = optional
                logger.debug("Characteristic %s has optional dependencies: %s", uuid, optional)

        return uuid_to_char, uuid_to_required_deps, uuid_to_optional_deps

    def _resolve_dependency_order(
        self,
        char_data: Mapping[str, bytes],
        uuid_to_required_deps: Mapping[str, list[str]],
        uuid_to_optional_deps: Mapping[str, list[str]],
    ) -> list[str]:
        """Topologically sort characteristics based on declared dependencies."""

        try:
            sorter: TopologicalSorter[str] = TopologicalSorter()
            for uuid in char_data:
                all_deps = uuid_to_required_deps.get(uuid, []) + uuid_to_optional_deps.get(uuid, [])
                batch_deps = [dep for dep in all_deps if dep in char_data]
                sorter.add(uuid, *batch_deps)

            sorted_sequence = sorter.static_order()
            sorted_uuids = list(sorted_sequence)
            logger.debug("Dependency-sorted parsing order: %s", sorted_uuids)
            return sorted_uuids
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Dependency sorting failed: %s. Using original order.", exc)
            return list(char_data.keys())

    def _find_missing_required_dependencies(
        self,
        uuid: str,
        required_deps: list[str],
        results: Mapping[str, CharacteristicData],
        base_ctx: CharacteristicContext | None,
    ) -> list[str]:
        """Determine which required dependencies are unavailable for a characteristic."""

        if not required_deps:
            return []

        missing: list[str] = []
        other_chars = base_ctx.other_characteristics if base_ctx and base_ctx.other_characteristics else None

        for dep_uuid in required_deps:
            if dep_uuid in results:
                if not results[dep_uuid].parse_success:
                    missing.append(dep_uuid)
                continue

            if other_chars and dep_uuid in other_chars:
                if not other_chars[dep_uuid].parse_success:
                    missing.append(dep_uuid)
                continue

            missing.append(dep_uuid)

        if missing:
            logger.debug("Characteristic %s missing required dependencies: %s", uuid, missing)

        return missing

    def _build_missing_dependency_failure(
        self,
        uuid: str,
        raw_data: bytes,
        characteristic: BaseCharacteristic | None,
        missing_required: list[str],
    ) -> CharacteristicData:
        """Create a failure result when required dependencies are absent."""

        char_name = characteristic.name if characteristic else "Unknown"
        error = MissingDependencyError(char_name, missing_required)
        logger.warning("Skipping %s due to missing required dependencies: %s", uuid, missing_required)

        if characteristic is not None:
            failure_info = characteristic.info
        else:
            fallback_info = self.get_characteristic_info(uuid)
            if fallback_info is not None:
                failure_info = fallback_info
            else:
                failure_info = CharacteristicInfo(
                    uuid=BluetoothUUID(uuid),
                    name=char_name,
                    description="",
                    value_type=ValueType.UNKNOWN,
                    unit="",
                    properties=[],
                )

        return CharacteristicData(
            info=failure_info,
            value=None,
            raw_data=raw_data,
            parse_success=False,
            error_message=str(error),
        )

    def _log_optional_dependency_gaps(
        self,
        uuid: str,
        optional_deps: list[str],
        results: Mapping[str, CharacteristicData],
        base_ctx: CharacteristicContext | None,
    ) -> None:
        """Emit debug logs when optional dependencies are unavailable."""

        if not optional_deps:
            return

        other_chars = base_ctx.other_characteristics if base_ctx and base_ctx.other_characteristics else None

        for dep_uuid in optional_deps:
            if dep_uuid in results:
                continue
            if other_chars and dep_uuid in other_chars:
                continue
            logger.debug("Optional dependency %s not available for %s", dep_uuid, uuid)

    def _build_parse_context(
        self,
        base_ctx: CharacteristicContext | None,
        results: Mapping[str, CharacteristicData],
    ) -> CharacteristicContext:
        """Construct the context passed to per-characteristic parsers."""

        results_mapping = cast(Mapping[str, CharacteristicDataProtocol], results)

        if base_ctx is not None:
            return CharacteristicContext(
                device_info=base_ctx.device_info,
                advertisement=base_ctx.advertisement,
                other_characteristics=results_mapping,
                raw_service=base_ctx.raw_service,
            )

        return CharacteristicContext(other_characteristics=results_mapping)

    def get_characteristics_info(self, uuids: list[str]) -> dict[str, CharacteristicInfo | None]:
        """Get information about multiple characteristics by UUID.

        Args:
            uuids: List of characteristic UUIDs

        Returns:
            Dictionary mapping UUIDs to CharacteristicInfo
            (or None if not found)
        """
        results: dict[str, CharacteristicInfo | None] = {}
        for uuid in uuids:
            results[uuid] = self.get_characteristic_info(uuid)
        return results

    def validate_characteristic_data(self, uuid: str, data: bytes) -> ValidationResult:
        """Validate characteristic data format against SIG specifications.

        Args:
            uuid: The characteristic UUID
            data: Raw data bytes to validate

        Returns:
            ValidationResult with validation details
        """
        try:
            # Attempt to parse the data - if it succeeds, format is valid
            parsed = self.parse_characteristic(uuid, data)
            return ValidationResult(
                uuid=BluetoothUUID(uuid),
                name=parsed.name,
                is_valid=parsed.parse_success,
                actual_length=len(data),
                error_message=parsed.error_message,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            # If parsing failed, data format is invalid
            return ValidationResult(
                uuid=BluetoothUUID(uuid),
                name="Unknown",
                is_valid=False,
                actual_length=len(data),
                error_message=str(e),
            )

    def get_service_characteristics(self, service_uuid: str) -> list[str]:  # pylint: disable=too-many-return-statements
        """Get the characteristic UUIDs associated with a service.

        Args:
            service_uuid: The service UUID

        Returns:
            List of characteristic UUIDs for this service
        """
        service_class = GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID(service_uuid))
        if not service_class:
            return []

        try:
            temp_service = service_class()
            required_chars = temp_service.get_required_characteristics()
            return [str(k) for k in required_chars]
        except Exception:  # pylint: disable=broad-exception-caught
            return []

    def register_custom_characteristic_class(
        self,
        uuid_or_name: str,
        cls: type[BaseCharacteristic],
        metadata: CharacteristicRegistration | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            uuid_or_name: The characteristic UUID or name
            cls: The characteristic class to register
            metadata: Optional metadata dataclass with name, unit, value_type, summary
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseCharacteristic
            ValueError: If UUID conflicts with existing registration and override=False
        """
        # Register the class
        CharacteristicRegistry.register_characteristic_class(uuid_or_name, cls, override)

        # Register metadata if provided
        if metadata:
            # Convert ValueType enum to string for registry storage
            vtype_str = metadata.value_type.value if hasattr(metadata.value_type, "value") else str(metadata.value_type)
            entry = CustomUuidEntry(
                uuid=metadata.uuid,
                name=metadata.name or cls.__name__,
                id=metadata.id,
                summary=metadata.summary,
                unit=metadata.unit,
                value_type=vtype_str,
            )
            uuid_registry.register_characteristic(entry, override)

    def register_custom_service_class(
        self,
        uuid_or_name: str,
        cls: type[BaseGattService],
        metadata: ServiceRegistration | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid_or_name: The service UUID or name
            cls: The service class to register
            metadata: Optional metadata dataclass with name, summary
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False
        """
        # Register the class
        GattServiceRegistry.register_service_class(uuid_or_name, cls, override)

        # Register metadata if provided
        if metadata:
            entry = CustomUuidEntry(
                uuid=metadata.uuid,
                name=metadata.name or cls.__name__,
                id=metadata.id,
                summary=metadata.summary,
            )
            uuid_registry.register_service(entry, override)


# Global instance for backward compatibility with gatt_manager
BluetoothSIG = BluetoothSIGTranslator()
