"""Bluetooth SIG GATT service registry.

This module contains the service registry implementation, including the
ServiceName enum, service class mappings, and the GattServiceRegistry
class. This was moved from __init__.py to follow Python best practices
of keeping __init__.py files lightweight.
"""

from __future__ import annotations

import threading
from functools import lru_cache

from typing_extensions import TypeGuard

from ...types.gatt_enums import ServiceName
from ...types.gatt_services import ServiceDiscoveryData
from ...types.uuid import BluetoothUUID
from ..registry_utils import ModuleDiscovery, TypeValidator
from ..uuid_registry import uuid_registry
from .base import BaseGattService

__all__ = [
    "ServiceName",
    "SERVICE_CLASS_MAP",
    "GattServiceRegistry",
]


class _ServiceClassValidator:  # pylint: disable=too-few-public-methods
    """Utility class for validating service classes.

    Note: Single-purpose validator class - pylint disable justified.
    """

    @staticmethod
    def is_service_subclass(candidate: object) -> TypeGuard[type[BaseGattService]]:
        """Return True when candidate is a BaseGattService subclass."""
        return TypeValidator.is_subclass_of(candidate, BaseGattService)


class _ServiceClassDiscovery:
    """Handles discovery and validation of service classes in the package."""

    _MODULE_EXCLUSIONS = {"__main__", "__init__", "base", "registry"}

    @classmethod
    def iter_module_names(cls) -> list[str]:
        """Return sorted service module names discovered via pkgutil.walk_packages."""
        package_name = __package__ or "bluetooth_sig.gatt.services"
        return ModuleDiscovery.iter_module_names(package_name, cls._MODULE_EXCLUSIONS)

    @classmethod
    def discover_classes(cls) -> list[type[BaseGattService]]:
        """Discover all concrete service classes defined in the package.

        Validates that discovered classes have required methods for proper operation.
        """
        module_names = cls.iter_module_names()
        return ModuleDiscovery.discover_classes(
            module_names,
            BaseGattService,
            _ServiceClassValidator.is_service_subclass,
        )


class _ServiceClassMapBuilder:
    """Builds and caches the service class map using dynamic discovery."""

    @staticmethod
    def build_enum_map() -> dict[ServiceName, type[BaseGattService]]:
        """Build the service class mapping using runtime discovery."""
        mapping: dict[ServiceName, type[BaseGattService]] = {}

        for service_cls in _ServiceClassDiscovery.discover_classes():
            # Get UUID from class
            try:
                uuid_obj = service_cls.get_class_uuid()
            except (AttributeError, ValueError):
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
                    f"Multiple service classes resolved for {enum_member.name}:"
                    f" {existing.__name__} and {service_cls.__name__}"
                )
            mapping[enum_member] = service_cls

        return mapping

    @staticmethod
    @lru_cache(maxsize=1)
    def get_cached_enum_map() -> dict[ServiceName, type[BaseGattService]]:
        """Return the cached enum-keyed service class map."""
        return _ServiceClassMapBuilder.build_enum_map()

    @staticmethod
    def clear_cache() -> None:
        """Clear the service class map cache."""
        _ServiceClassMapBuilder.get_cached_enum_map.cache_clear()


# Public API functions for backward compatibility
def get_service_class_map() -> dict[ServiceName, type[BaseGattService]]:
    """Get the service class map, building it if necessary."""
    return _ServiceClassMapBuilder.get_cached_enum_map()


# Public API - backward compatibility globals
SERVICE_CLASS_MAP = _ServiceClassMapBuilder.get_cached_enum_map()


class GattServiceRegistry:
    """Registry for all supported GATT services."""

    _lock = threading.RLock()
    _custom_service_classes: dict[BluetoothUUID, type[BaseGattService]] = {}

    @classmethod
    def register_service_class(cls, uuid: str | BluetoothUUID, service_cls: object, override: bool = False) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid: The service UUID
            service_cls: The service class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If service_cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False
        """
        # Runtime safety check retained in case of dynamic caller misuse despite type hints.
        if not _ServiceClassValidator.is_service_subclass(service_cls):
            raise TypeError(f"Class {service_cls!r} must inherit from BaseGattService")

        # Always normalize UUID to BluetoothUUID
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid

        with cls._lock:
            # Check for conflicts
            if not override:
                if bt_uuid in cls._custom_service_classes:
                    raise ValueError(f"UUID {bt_uuid} already registered. Use override=True to replace.")

            cls._custom_service_classes[bt_uuid] = service_cls

    @classmethod
    def unregister_service_class(cls, uuid: str | BluetoothUUID) -> None:
        """Unregister a custom service class.

        Args:
            uuid: The service UUID to unregister
        """
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        with cls._lock:
            cls._custom_service_classes.pop(bt_uuid, None)

    @classmethod
    def _get_services(cls) -> list[type[BaseGattService]]:
        """Get the list of service classes."""
        return list(get_service_class_map().values())

    @classmethod
    def get_service_class(cls, uuid: str | BluetoothUUID) -> type[BaseGattService] | None:
        """Get the service class for a given UUID."""
        try:
            if isinstance(uuid, str):
                bt_uuid = BluetoothUUID(uuid)
            else:
                bt_uuid = uuid
        except ValueError:
            return None
        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_service_classes.get(bt_uuid):
                return custom_cls

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
        return get_service_class_map().get(name)

    @classmethod
    def get_service_class_by_uuid(cls, uuid: BluetoothUUID) -> type[BaseGattService] | None:
        """Get the service class for a given UUID (alias for
        get_service_class)."""
        return cls.get_service_class(uuid)

    @classmethod
    def create_service(cls, uuid: BluetoothUUID, characteristics: ServiceDiscoveryData) -> BaseGattService | None:
        """Create a service instance for the given UUID and characteristics.

        Args:
            uuid: Service UUID
            characteristics: Dict mapping characteristic UUIDs to CharacteristicInfo

        Returns:
            Service instance if found, None otherwise
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
        return cls._get_services().copy()

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
        with cls._lock:
            cls._custom_service_classes.clear()
