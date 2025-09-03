"""Core Bluetooth SIG standards translator functionality."""

from typing import Any, Dict, Optional

from .gatt.characteristics import CharacteristicRegistry
from .gatt.services import GattServiceRegistry


class BluetoothSIGTranslator:
    """Pure Bluetooth SIG standards translator for characteristic and service interpretation."""

    def __init__(self):
        """Initialize the SIG translator."""
        pass

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
        characteristic = CharacteristicRegistry.create_characteristic(uuid, properties=set(), **kwargs)

        if characteristic:
            try:
                return characteristic.parse_value(bytearray(raw_data))
            except Exception:
                # If parsing fails, return raw data
                return raw_data

        # No parser found, return raw data
        return raw_data

    def get_characteristic_info(self, uuid: str) -> Optional[Dict[str, Any]]:
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
                "device_class": temp_char.device_class,
                "state_class": temp_char.state_class,
            }
        except Exception:
            return None

    def get_service_info(self, uuid: str) -> Optional[Dict[str, Any]]:
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
        except Exception:
            return None

    def list_supported_characteristics(self) -> Dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs
        """
        result = {}
        for name, char_class in CharacteristicRegistry._characteristics.items():
            try:
                temp_char = char_class(uuid="", properties=set())
                result[name] = temp_char.CHAR_UUID
            except Exception:
                continue
        return result

    def list_supported_services(self) -> Dict[str, str]:
        """List all supported services with their names and UUIDs.

        Returns:
            Dictionary mapping service names to UUIDs
        """
        result = {}
        for service_class in GattServiceRegistry._services:
            try:
                temp_service = service_class(uuid="")
                service_name = getattr(temp_service, "_service_name", service_class.__name__)
                result[service_name] = temp_service.SERVICE_UUID
            except Exception:
                continue
        return result
