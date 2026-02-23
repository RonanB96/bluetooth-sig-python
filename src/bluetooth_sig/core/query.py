"""Characteristic and service query engine.

Provides read-only lookup and metadata retrieval for characteristics and services
using the SIG registries. Stateless — no mutable state.
"""

from __future__ import annotations

import logging

from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.services import ServiceName
from ..gatt.services.registry import GattServiceRegistry
from ..gatt.uuid_registry import uuid_registry
from ..types import (
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
)
from ..types.gatt_enums import CharacteristicName
from ..types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class CharacteristicQueryEngine:
    """Stateless query engine for characteristic and service metadata.

    Provides all read-only lookup operations: supports, get_value_type,
    get_*_info_*, list_supported_*, get_service_characteristics, get_sig_info_*.
    """

    def supports(self, uuid: str) -> bool:
        """Check if a characteristic UUID is supported.

        Args:
            uuid: The characteristic UUID to check

        Returns:
            True if the characteristic has a parser/encoder, False otherwise

        """
        try:
            bt_uuid = BluetoothUUID(uuid)
            char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
        except (ValueError, TypeError):
            return False
        else:
            return char_class is not None

    def get_value_type(self, uuid: str) -> type | str | None:
        """Get the expected Python type for a characteristic.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            Python type if characteristic is found, None otherwise

        """
        info = self.get_characteristic_info_by_uuid(uuid)
        return info.python_type if info else None

    def get_characteristic_info_by_uuid(self, uuid: str) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

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

        try:
            temp_char = char_class()
        except (TypeError, ValueError, AttributeError):
            return None
        else:
            return temp_char.info

    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum.

        Args:
            name: CharacteristicName enum

        Returns:
            Characteristic UUID or None if not found

        """
        info = self.get_characteristic_info_by_name(name)
        return info.uuid if info else None

    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum.

        Args:
            name: Service name or enum

        Returns:
            Service UUID or None if not found

        """
        name_str = name.value if isinstance(name, ServiceName) else name
        info = self.get_service_info_by_name(name_str)
        return info.uuid if info else None

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> CharacteristicInfo | None:
        """Get characteristic info by enum name.

        Args:
            name: CharacteristicName enum

        Returns:
            CharacteristicInfo if found, None otherwise

        """
        char_class = CharacteristicRegistry.get_characteristic_class(name)
        if not char_class:
            return None

        info = char_class.get_configured_info()
        if info:
            return info

        try:
            temp_char = char_class()
        except (TypeError, ValueError, AttributeError):
            return None
        else:
            return temp_char.info

    def get_service_info_by_name(self, name: str | ServiceName) -> ServiceInfo | None:
        """Get service info by name or enum instead of UUID.

        Args:
            name: Service name string or ServiceName enum

        Returns:
            ServiceInfo if found, None otherwise

        """
        name_str = name.value if isinstance(name, ServiceName) else name

        try:
            uuid_info = uuid_registry.get_service_info(name_str)
            if uuid_info:
                return ServiceInfo(uuid=uuid_info.uuid, name=uuid_info.name, characteristics=[])
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to look up service info for name=%s", name_str, exc_info=True)

        return None

    def get_service_info_by_uuid(self, uuid: str) -> ServiceInfo | None:
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
            char_infos: list[CharacteristicInfo] = []
            for _, char_instance in temp_service.characteristics.items():
                char_infos.append(char_instance.info)
            return ServiceInfo(
                uuid=temp_service.uuid,
                name=temp_service.name,
                characteristics=char_infos,
            )
        except (TypeError, ValueError, AttributeError):
            return None

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs

        """
        result: dict[str, str] = {}
        for name, char_class in CharacteristicRegistry.get_all_characteristics().items():
            configured_info = char_class.get_configured_info()
            if configured_info:
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

    def get_characteristics_info_by_uuids(self, uuids: list[str]) -> dict[str, CharacteristicInfo | None]:
        """Get information about multiple characteristics by UUID.

        Args:
            uuids: List of characteristic UUIDs

        Returns:
            Dictionary mapping UUIDs to CharacteristicInfo (or None if not found)

        """
        results: dict[str, CharacteristicInfo | None] = {}
        for uuid in uuids:
            results[uuid] = self.get_characteristic_info_by_uuid(uuid)
        return results

    def get_service_characteristics(self, service_uuid: str) -> list[str]:
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

    def get_sig_info_by_name(self, name: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a characteristic or service by name.

        Args:
            name: Characteristic or service name

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        try:
            char_info = uuid_registry.get_characteristic_info(name)
            if char_info:
                return CharacteristicInfo(
                    uuid=char_info.uuid,
                    name=char_info.name,
                    python_type=char_info.python_type,
                    unit=char_info.unit or "",
                )
        except (KeyError, ValueError, AttributeError):
            logger.warning("Failed to look up SIG info by name: %s", name)

        service_info = self.get_service_info_by_name(name)
        if service_info:
            return service_info

        return None

    def get_sig_info_by_uuid(self, uuid: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a UUID.

        Args:
            uuid: UUID string (with or without dashes)

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        char_info = self.get_characteristic_info_by_uuid(uuid)
        if char_info:
            return char_info

        service_info = self.get_service_info_by_uuid(uuid)
        if service_info:
            return service_info

        return None
