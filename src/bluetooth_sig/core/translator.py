"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

from typing import Any

from ..gatt.characteristics import CharacteristicName, CharacteristicRegistry
from ..gatt.context import CharacteristicContext
from ..gatt.services import GattServiceRegistry, ServiceName
from ..gatt.services.base import BaseGattService
from ..types import (
    CharacteristicData,
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
    ValidationResult,
)


class BluetoothSIGTranslator:
    """Pure Bluetooth SIG standards translator for characteristic and service
    interpretation."""

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
        properties: set[str] | None = None,
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
        # Create characteristic instance for parsing. Pass explicit properties
        # rather than arbitrary kwargs to keep the API clear and type-safe.
        characteristic = CharacteristicRegistry.create_characteristic(
            uuid, properties=properties or set()
        )

        if characteristic:
            # Use the parse_value method; pass context when provided.
            result = characteristic.parse_value(raw_data, ctx)

            # Attach context if available and result doesn't already have it
            if ctx is not None:
                result.source_context = ctx
            return result

        # No parser found, return fallback result
        return CharacteristicData(
            uuid=uuid,
            name="Unknown",
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
        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(uuid)
        if not char_class:
            return None

        # Create temporary instance to get metadata
        try:
            temp_char = char_class(uuid=uuid, properties=set())
            return CharacteristicInfo(
                uuid=temp_char.char_uuid,
                name=getattr(temp_char, "_characteristic_name", char_class.__name__),
                value_type=getattr(temp_char, "value_type", ""),
                unit=temp_char.unit,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_characteristic_uuid(self, name: str | CharacteristicName) -> str | None:
        """Get the UUID for a characteristic name or enum.

        Args:
            name: Characteristic name or enum

        Returns:
            Characteristic UUID or None if not found
        """
        # Handle enum input
        if isinstance(name, CharacteristicName):
            char_name: str | CharacteristicName = name
        else:
            char_name = name

        # Try to find the characteristic by name in the registry
        char_class = CharacteristicRegistry.get_characteristic_class(char_name)
        if char_class:
            # Create temporary instance to get UUID
            try:
                temp_char = char_class(uuid="", properties=set())
                return temp_char.char_uuid
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
        # Handle enum input
        if isinstance(name, ServiceName):
            service_name: str | ServiceName = name
        else:
            service_name = name

        # Try to find the service by name
        service_class = GattServiceRegistry.get_service_class_by_name(service_name)
        if service_class:
            try:
                temp_service = service_class()
                return temp_service.SERVICE_UUID
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        return None

    def get_characteristic_info_by_name(self, name: str) -> CharacteristicInfo | None:
        """Get characteristic info by name instead of UUID.

        Args:
            name: Characteristic name

        Returns:
            CharacteristicInfo if found, None otherwise
        """
        # Try to find the characteristic by name in the registry
        char_class = CharacteristicRegistry.get_characteristic_class(name)
        if char_class:
            try:
                temp_char = char_class(uuid="", properties=set())
                return CharacteristicInfo(
                    uuid=temp_char.char_uuid,
                    name=getattr(
                        temp_char, "_characteristic_name", char_class.__name__
                    ),
                    value_type=getattr(temp_char, "value_type", ""),
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
        from ..gatt.uuid_registry import (  # pylint: disable=import-outside-toplevel
            uuid_registry,
        )

        try:
            uuid_info = uuid_registry.get_service_info(name)
            if uuid_info:
                return ServiceInfo(
                    uuid=uuid_info.uuid, name=uuid_info.name, characteristics=[]
                )
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
                uuid=temp_service.SERVICE_UUID,
                name=temp_service.name,
                characteristics=getattr(temp_service, "characteristics", []),
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
                result[name] = temp_char.char_uuid
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
                service_name = getattr(
                    temp_service, "_service_name", service_class.__name__
                )
                result[service_name] = temp_service.SERVICE_UUID
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def process_services(self, services: dict[str, dict[str, dict[str, Any]]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics
        """
        for uuid, service_data in services.items():
            service = GattServiceRegistry.create_service(
                uuid, service_data.get("characteristics", {})
            )
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
        # Try characteristic first
        char_info = self.get_characteristic_info_by_name(name)
        if char_info:
            return char_info

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
        """Parse multiple characteristics at once.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional base `CharacteristicContext` used as the starting
                device-level context for each parsed characteristic.

        Returns:
            Dictionary mapping UUIDs to CharacteristicData results
        """
        base_ctx = ctx

        results: dict[str, CharacteristicData] = {}
        for uuid, raw_data in char_data.items():
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

        return results

    def get_characteristics_info(
        self, uuids: list[str]
    ) -> dict[str, CharacteristicInfo | None]:
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
            required_chars = getattr(temp_service, "get_required_characteristics", None)
            if callable(required_chars):
                req = required_chars()
                if isinstance(req, dict):
                    return [str(k) for k in req]
                try:
                    return [str(x) for x in req]
                except Exception:  # pylint: disable=broad-exception-caught
                    return []
            chars = getattr(temp_service, "characteristics", None)
            if isinstance(chars, (list, tuple)):
                return [str(x) for x in chars]
            return []
        except Exception:  # pylint: disable=broad-exception-caught
            return []


# Global instance for backward compatibility with gatt_manager
BluetoothSIG = BluetoothSIGTranslator()
