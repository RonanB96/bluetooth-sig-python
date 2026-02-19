"""Bluetooth SIG GATT service registry.

This module contains the service registry implementation, including the
ServiceName enum, service class mappings, and the GattServiceRegistry
class. This was moved from __init__.py to follow Python best practices
of keeping __init__.py files lightweight.
"""

from __future__ import annotations

from typing import ClassVar, TypeGuard

from ...registry.base import BaseUUIDClassRegistry
from ...types.gatt_enums import ServiceName
from ...types.gatt_services import ServiceDiscoveryData
from ...types.uuid import BluetoothUUID
from ..exceptions import UUIDResolutionError
from ..registry_utils import ModuleDiscovery, TypeValidator
from ..uuid_registry import uuid_registry
from .base import BaseGattService

__all__ = [
    "GattServiceRegistry",
    "ServiceName",
    "get_service_class_map",
]


def _is_service_subclass(candidate: object) -> TypeGuard[type[BaseGattService]]:
    """Type guard to check if candidate is a BaseGattService subclass.

    Args:
        candidate: Object to check

    Returns:
        True if candidate is a subclass of BaseGattService
    """
    return TypeValidator.is_subclass_of(candidate, BaseGattService)


def get_service_class_map() -> dict[ServiceName, type[BaseGattService]]:
    """Get the current service class map.

    Returns:
        Dictionary mapping ServiceName enum to service classes
    """
    return GattServiceRegistry.get_instance()._get_enum_map()  # pylint: disable=protected-access


class GattServiceRegistry(BaseUUIDClassRegistry[ServiceName, BaseGattService]):
    """Registry for all supported GATT services."""

    _MODULE_EXCLUSIONS: ClassVar[set[str]] = {"__main__", "__init__", "base", "registry"}

    def _get_base_class(self) -> type[BaseGattService]:
        """Return the base class for service validation."""
        return BaseGattService

    def _discover_sig_classes(self) -> list[type[BaseGattService]]:
        """Discover all SIG-defined service classes in the package."""
        package_name = __package__ or "bluetooth_sig.gatt.services"
        module_names = ModuleDiscovery.iter_module_names(package_name, self._MODULE_EXCLUSIONS)

        return ModuleDiscovery.discover_classes(
            module_names,
            BaseGattService,
            _is_service_subclass,
        )

    def _build_enum_map(self) -> dict[ServiceName, type[BaseGattService]]:
        """Build the enum → class mapping using runtime discovery."""
        mapping: dict[ServiceName, type[BaseGattService]] = {}

        for service_cls in self._discover_sig_classes():
            try:
                uuid_obj = service_cls.get_class_uuid()
            except (AttributeError, ValueError, UUIDResolutionError):
                # Skip classes that can't resolve a UUID (e.g., abstract base classes)
                continue

            # Find the corresponding enum member by UUID
            enum_member = None
            for candidate_enum in ServiceName:
                candidate_info = uuid_registry.get_service_info(candidate_enum.value)
                if candidate_info and candidate_info.uuid == uuid_obj:
                    enum_member = candidate_enum
                    break

            if enum_member is None:
                continue

            existing = mapping.get(enum_member)
            if existing is not None and existing is not service_cls:
                raise RuntimeError(
                    f"Multiple service classes resolved for {enum_member.name}: "
                    f"{existing.__name__} and {service_cls.__name__}"
                )
            mapping[enum_member] = service_cls

        return mapping

    def _load(self) -> None:
        """Perform the actual loading of registry data."""
        _ = self._get_enum_map()
        _ = self._get_sig_classes_map()
        self._loaded = True

    # Backward compatibility aliases

    @classmethod
    def register_service_class(
        cls, uuid: str | BluetoothUUID | int, service_cls: type[BaseGattService], override: bool = False
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid: The service UUID
            service_cls: The service class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If service_cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False
        """
        instance = cls.get_instance()
        instance.register_class(uuid, service_cls, override)

    @classmethod
    def unregister_service_class(cls, uuid: str | BluetoothUUID | int) -> None:
        """Unregister a custom service class.

        Args:
            uuid: The service UUID to unregister
        """
        instance = cls.get_instance()
        instance.unregister_class(uuid)

    @classmethod
    def _get_services(cls) -> list[type[BaseGattService]]:
        """Get the list of service classes."""
        instance = cls.get_instance()
        return list(instance._get_enum_map().values())  # pylint: disable=protected-access

    @classmethod
    def get_service_class(cls, uuid: str | BluetoothUUID | int) -> type[BaseGattService] | None:
        """Get the service class for a given UUID.

        Args:
            uuid: The service UUID

        Returns:
            Service class if found, None otherwise

        Raises:
            ValueError: If uuid format is invalid
        """
        # Normalize to BluetoothUUID (let ValueError propagate)
        bt_uuid = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)

        instance = cls.get_instance()
        service_cls = instance.get_class_by_uuid(bt_uuid)
        if service_cls:
            return service_cls

        # Fallback: check if any service matches this UUID via matches_uuid()
        for service_class in cls._get_services():
            if service_class.matches_uuid(bt_uuid):
                return service_class
        return None

    @classmethod
    def get_service_class_by_name(cls, name: str | ServiceName) -> type[BaseGattService] | None:
        """Get the service class for a given name or enum."""
        if isinstance(name, str):
            # For string names, find the matching enum member
            for enum_member in ServiceName:
                if enum_member.value == name:
                    name = enum_member
                    break
            else:
                return None  # No matching enum found

        instance = cls.get_instance()
        return instance.get_class_by_enum(name)

    @classmethod
    def get_service_class_by_uuid(cls, uuid: str | BluetoothUUID | int) -> type[BaseGattService] | None:
        """Get the service class for a given UUID (alias for get_service_class)."""
        return cls.get_service_class(uuid)

    @classmethod
    def create_service(
        cls, uuid: str | BluetoothUUID | int, characteristics: ServiceDiscoveryData
    ) -> BaseGattService | None:
        """Create a service instance for the given UUID and characteristics.

        Args:
            uuid: Service UUID
            characteristics: Dict mapping characteristic UUIDs to CharacteristicInfo

        Returns:
            Service instance if found, None otherwise

        Raises:
            ValueError: If uuid format is invalid
        """
        service_class = cls.get_service_class(uuid)
        if not service_class:
            return None

        service = service_class()
        service.process_characteristics(characteristics)
        return service

    @classmethod
    def get_all_services(cls) -> list[type[BaseGattService]]:
        """Get all registered service classes.

        Returns:
            List of all registered service classes

        """
        return cls._get_services()

    @classmethod
    def supported_services(cls) -> list[str]:
        """Get a list of supported service UUIDs."""
        return [str(service().uuid) for service in cls._get_services()]

    @classmethod
    def supported_service_names(cls) -> list[str]:
        """Get a list of supported service names."""
        return [e.value for e in ServiceName]

    @classmethod
    def clear_custom_registrations(cls) -> None:
        """Clear all custom service registrations (for testing)."""
        instance = cls.get_instance()
        for uuid in list(instance.list_custom_uuids()):
            instance.unregister_class(uuid)
