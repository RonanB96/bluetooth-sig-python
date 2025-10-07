"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

import logging
from graphlib import TopologicalSorter
from typing import Any

from ..gatt.characteristics import CharacteristicName, CharacteristicRegistry
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.context import CharacteristicContext
from ..gatt.services import SERVICE_CLASS_MAP, GattServiceRegistry, ServiceName
from ..gatt.services.base import BaseGattService
from ..gatt.uuid_registry import CustomUuidEntry, uuid_registry
from ..types import (
    CharacteristicData,
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
    ) -> CharacteristicData:
        """Parse a characteristic's raw data using SIG standards.

        Args:
            uuid: The characteristic UUID (with or without dashes)
            raw_data: Raw bytes from the characteristic
            ctx: Optional `CharacteristicContext` providing device-level info
                and previously-parsed characteristics to the parser.
            properties: Optional set of characteristic properties to pass when
                constructing the characteristic instance.

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
            try:
                temp_char = char_class(uuid="", properties=set())
                value_type_str = (
                    temp_char.value_type.value if hasattr(temp_char.value_type, "value") else str(temp_char.value_type)
                )
                return CharacteristicInfo(
                    uuid=temp_char.uuid,
                    name=getattr(temp_char, "_characteristic_name", char_class.__name__),
                    value_type=value_type_str,
                    unit=temp_char.unit,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                pass
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
        service_class = GattServiceRegistry.get_service_class_by_uuid(uuid)
        if not service_class:
            return None

        try:
            temp_service = service_class()
            return ServiceInfo(
                uuid=temp_service.uuid,
                name=temp_service.name,
                characteristics=[str(uuid) for uuid in temp_service.characteristics.keys()],
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs
        """
        result: dict[str, str] = {}
        for (
            name,
            char_class,
        ) in CharacteristicRegistry.get_all_characteristics().items():
            try:
                temp_char = char_class(uuid="", properties=set())
                result[name] = temp_char.uuid
            except Exception:  # pylint: disable=broad-exception-caught
                continue
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
                result[service_name] = temp_service.uuid
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def process_services(self, services: dict[str, dict[str, dict[str, Any]]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics
        """
        for uuid, service_data in services.items():
            service = GattServiceRegistry.create_service(uuid, service_data.get("characteristics", {}))
            if service:
                self._services[uuid] = service

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
                # Build CharacteristicInfo
                return CharacteristicInfo(
                    uuid=char_info.uuid,
                    name=char_info.name,
                    value_type="",
                    unit="",
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
        The parsing order is determined by the `dependencies` attribute declared on
        characteristic classes.

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

        # Resolve dependencies for each characteristic
        uuid_to_dependencies: dict[str, list[str]] = {}
        for uuid in char_data.keys():
            characteristic = CharacteristicRegistry.create_characteristic(uuid)
            if characteristic and characteristic.dependencies:
                uuid_to_dependencies[uuid] = characteristic.dependencies
                logger.debug("Characteristic %s has dependencies: %s", uuid, characteristic.dependencies)

        # Sort characteristics by dependencies (topological sort using graphlib)
        try:
            # Build graph for TopologicalSorter: {node: {predecessors}}
            # Note: Don't use TopologicalSorter[str]() - not compatible with Python 3.9
            ts = TopologicalSorter()
            for uuid in char_data.keys():
                deps = uuid_to_dependencies.get(uuid, [])
                # Filter to only include dependencies that are in this batch
                batch_deps = [dep for dep in deps if dep in char_data]
                ts.add(uuid, *batch_deps)

            sorted_uuids = list(ts.static_order())
            logger.debug("Dependency-sorted parsing order: %s", sorted_uuids)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Dependency sorting failed: %s. Using original order.", e)
            sorted_uuids = list(char_data.keys())

        results: dict[str, CharacteristicData] = {}
        for uuid in sorted_uuids:
            raw_data = char_data[uuid]
            # Build a context for this parse that shares device-level info
            # from the base context but provides the current results mapping
            # so parsers can look up previously-parsed characteristics.
            if base_ctx is not None:
                per_call_ctx = CharacteristicContext(
                    device_info=base_ctx.device_info,
                    advertisement=base_ctx.advertisement,
                    other_characteristics=results,
                    raw_service=base_ctx.raw_service,
                )
            else:
                per_call_ctx = CharacteristicContext(other_characteristics=results)

            results[uuid] = self.parse_characteristic(uuid, raw_data, ctx=per_call_ctx)

        logger.debug("Batch parsing complete: %d results", len(results))
        return results

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
                uuid=uuid,
                name=parsed.name,
                is_valid=parsed.parse_success,
                actual_length=len(data),
                error_message=parsed.error_message,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            # If parsing failed, data format is invalid
            return ValidationResult(
                uuid=uuid,
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
        service_class = GattServiceRegistry.get_service_class_by_uuid(service_uuid)
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
            entry = CustomUuidEntry(
                uuid=metadata.uuid,
                name=metadata.name or cls.__name__,
                id=metadata.id,
                summary=metadata.summary,
                unit=metadata.unit,
                value_type=metadata.value_type,
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
