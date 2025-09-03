"""Core Bluetooth SIG standards translator functionality."""

from typing import Any, Optional

from .gatt.characteristics import CharacteristicRegistry
from .gatt.services import GattServiceRegistry
from .gatt.services.base import BaseGattService


class BluetoothSIGTranslator:
    """Pure Bluetooth SIG standards translator for characteristic and service interpretation."""

    def __init__(self):
        """Initialize the SIG translator."""
        self._services: dict[str, BaseGattService] = {}

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    def parse_characteristic(self, uuid: str, raw_data: bytes, **kwargs) -> Any:
        """Parse a characteristic's raw data using SIG standards.

        Args:
            uuid: The characteristic UUID (with or without dashes)
            raw_data: Raw bytes from the characteristic
            **kwargs: Additional parameters for characteristic creation

        Returns:
            Parsed value according to SIG standards, or raw_data if no parser found
        """
        # Create characteristic instance for parsing
        characteristic = CharacteristicRegistry.create_characteristic(
            uuid, properties=set(), **kwargs
        )

        if characteristic:
            try:
                return characteristic.parse_value(bytearray(raw_data))
            except Exception:  # pylint: disable=broad-exception-caught
                # If parsing fails, return raw data
                return raw_data

        # No parser found, return raw data
        return raw_data

    def get_characteristic_info(self, uuid: str) -> Optional[dict[str, Any]]:
        """Get information about a characteristic by UUID.

        Args:
            uuid: The characteristic UUID

        Returns:
            Dictionary with characteristic metadata or None if not found
        """
        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(uuid)
        if not char_class:
            return None

        # Create temporary instance to get metadata
        try:
            temp_char = char_class(uuid=uuid, properties=set())
            return {
                "name": getattr(temp_char, "_characteristic_name", char_class.__name__),
                "uuid": temp_char.CHAR_UUID,
                "value_type": getattr(temp_char, "value_type", "unknown"),
                "unit": temp_char.unit,
            }
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_service_info(self, uuid: str) -> Optional[dict[str, Any]]:
        """Get information about a service by UUID.

        Args:
            uuid: The service UUID

        Returns:
            Dictionary with service metadata or None if not found
        """
        service_class = GattServiceRegistry.get_service_class_by_uuid(uuid)
        if not service_class:
            return None

        try:
            temp_service = service_class(uuid=uuid)
            return {
                "name": getattr(temp_service, "_service_name", service_class.__name__),
                "uuid": temp_service.SERVICE_UUID,
                "characteristics": getattr(temp_service, "characteristics", []),
            }
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


# Global instance for backward compatibility with gatt_manager
gatt_hierarchy = BluetoothSIGTranslator()
