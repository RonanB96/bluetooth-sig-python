"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .gatt.characteristics import CharacteristicRegistry
from .gatt.services import GattServiceRegistry
from .gatt.services.base import BaseGattService


@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: str
    name: str
    description: str | None = None


@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""

    value_type: str | None = None
    unit: str | None = None
    properties: list[str] | None = None


@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[str] | None = None


@dataclass
class ParsedData(CharacteristicInfo):
    """Result of parsing characteristic data."""

    value: Any | None = None
    raw_data: bytes | None = None
    parse_success: bool = True
    error_message: str | None = None


@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str | None = None


class BluetoothSIGTranslator:
    """Pure Bluetooth SIG standards translator for characteristic and service
    interpretation."""

    def __init__(self):
        """Initialize the SIG translator."""
        self._services: dict[str, BaseGattService] = {}

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    def parse_characteristic(self, uuid: str, raw_data: bytes, **kwargs) -> ParsedData:
        """Parse a characteristic's raw data using SIG standards.

        Args:
            uuid: The characteristic UUID (with or without dashes)
            raw_data: Raw bytes from the characteristic
            **kwargs: Additional parameters for characteristic creation

        Returns:
            ParsedData with parsed value and metadata
        """
        # Create characteristic instance for parsing
        characteristic = CharacteristicRegistry.create_characteristic(
            uuid, properties=set(), **kwargs
        )

        if characteristic:
            try:
                parsed_value = characteristic.parse_value(bytearray(raw_data))
                return ParsedData(
                    uuid=characteristic.CHAR_UUID,
                    name=getattr(
                        characteristic,
                        "_characteristic_name",
                        characteristic.__class__.__name__,
                    ),
                    value=parsed_value,
                    unit=characteristic.unit,
                    value_type=getattr(characteristic, "value_type", None),
                    raw_data=raw_data,
                    parse_success=True,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                # If parsing fails, return error result
                return ParsedData(
                    uuid=uuid,
                    name=getattr(
                        characteristic,
                        "_characteristic_name",
                        characteristic.__class__.__name__,
                    ),
                    value=raw_data,
                    raw_data=raw_data,
                    parse_success=False,
                    error_message=str(e),
                )

        # No parser found, return fallback result
        return ParsedData(
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
                uuid=temp_char.CHAR_UUID,
                name=getattr(temp_char, "_characteristic_name", char_class.__name__),
                value_type=getattr(temp_char, "value_type", None),
                unit=temp_char.unit,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_characteristic_info_by_name(self, name: str) -> CharacteristicInfo | None:
        """Get characteristic info by name instead of UUID.

        Args:
            name: Characteristic name

        Returns:
            CharacteristicInfo if found, None otherwise
        """
        # Try to find the characteristic by name in the registry
        for (
            char_name,
            char_class,
        ) in CharacteristicRegistry.get_all_characteristics().items():
            if char_name.lower() == name.lower():
                try:
                    temp_char = char_class(uuid="", properties=set())
                    return CharacteristicInfo(
                        uuid=temp_char.CHAR_UUID,
                        name=getattr(
                            temp_char, "_characteristic_name", char_class.__name__
                        ),
                        value_type=getattr(temp_char, "value_type", None),
                        unit=temp_char.unit,
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    continue
        return None

    def get_service_info_by_name(self, name: str) -> ServiceInfo | None:
        """Get service info by name instead of UUID.

        Args:
            name: Service name

        Returns:
            ServiceInfo if found, None otherwise
        """
        # Try to find the service by name in the registry
        for service_class in GattServiceRegistry.get_all_services():
            try:
                temp_service = service_class(uuid="")
                service_name = getattr(
                    temp_service, "_service_name", service_class.__name__
                )
                if service_name.lower() == name.lower():
                    return ServiceInfo(
                        uuid=temp_service.SERVICE_UUID,
                        name=service_name,
                        characteristics=getattr(temp_service, "characteristics", None),
                    )
            except Exception:  # pylint: disable=broad-exception-caught
                continue
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
            temp_service = service_class(uuid=uuid)
            return ServiceInfo(
                uuid=temp_service.SERVICE_UUID,
                name=getattr(temp_service, "_service_name", service_class.__name__),
                characteristics=getattr(temp_service, "characteristics", None),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs
        """
        result = {}
        for (
            name,
            char_class,
        ) in CharacteristicRegistry.get_all_characteristics().items():
            try:
                temp_char = char_class(uuid="", properties=set())
                result[name] = temp_char.CHAR_UUID
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def list_supported_services(self) -> dict[str, str]:
        """List all supported services with their names and UUIDs.

        Returns:
            Dictionary mapping service names to UUIDs
        """
        result = {}
        for service_class in GattServiceRegistry.get_all_services():
            try:
                temp_service = service_class(uuid="")
                service_name = getattr(
                    temp_service, "_service_name", service_class.__name__
                )
                result[service_name] = temp_service.SERVICE_UUID
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def process_services(self, services: dict[str, dict[str, dict]]) -> None:
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
        self, char_data: dict[str, bytes], **kwargs
    ) -> dict[str, ParsedData]:
        """Parse multiple characteristics at once.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            **kwargs: Additional parameters for characteristic creation

        Returns:
            Dictionary mapping UUIDs to ParsedData results
        """
        results = {}
        for uuid, raw_data in char_data.items():
            results[uuid] = self.parse_characteristic(uuid, raw_data, **kwargs)
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
        results = {}
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

    def get_service_characteristics(self, service_uuid: str) -> list[str]:
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
            temp_service = service_class(uuid=service_uuid)
            required_chars = getattr(temp_service, "get_required_characteristics", None)
            if required_chars and callable(required_chars):
                return list(required_chars().keys())
            return []
        except Exception:  # pylint: disable=broad-exception-caught
            return []


# Global instance for backward compatibility with gatt_manager
gatt_hierarchy = BluetoothSIGTranslator()
