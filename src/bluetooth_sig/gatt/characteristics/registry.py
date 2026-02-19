"""Bluetooth SIG GATT characteristic registry.

This module contains the characteristic registry implementation and
class mappings. CharacteristicName enum is now centralized in
types.gatt_enums to avoid circular imports.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar, TypeGuard

from ...registry.base import BaseUUIDClassRegistry
from ...types.gatt_enums import CharacteristicName
from ...types.uuid import BluetoothUUID
from ..registry_utils import ModuleDiscovery, TypeValidator
from ..resolver import NameVariantGenerator
from ..uuid_registry import uuid_registry
from .base import BaseCharacteristic

# Export for other modules to import
__all__ = ["CharacteristicName", "CharacteristicRegistry", "get_characteristic_class_map"]


def _is_characteristic_subclass(candidate: object) -> TypeGuard[type[BaseCharacteristic[Any]]]:
    """Type guard to check if candidate is a BaseCharacteristic subclass.

    Args:
        candidate: Object to check

    Returns:
        True if candidate is a subclass of BaseCharacteristic
    """
    return TypeValidator.is_subclass_of(candidate, BaseCharacteristic)


class _RegistryKeyBuilder:
    """Builds registry lookup keys for characteristics."""

    _NON_ALPHANUMERIC_RE = re.compile(r"[^a-z0-9]+")

    # Special cases for characteristics whose YAML names don't match enum display names
    # NOTE: CO2 uses LaTeX formatting in official Bluetooth SIG spec: "CO\textsubscript{2} Concentration"
    _SPECIAL_INFO_NAME_TO_ENUM: ClassVar[dict[str, CharacteristicName]] = {
        "CO\\textsubscript{2} Concentration": CharacteristicName.CO2_CONCENTRATION,
    }

    @classmethod
    def slugify_characteristic_identifier(cls, value: str) -> str:
        """Convert a characteristic display name into an org.bluetooth identifier slug."""
        return cls._NON_ALPHANUMERIC_RE.sub("_", value.lower()).strip("_")

    @classmethod
    def generate_candidate_keys(cls, enum_member: CharacteristicName) -> list[str]:
        """Generate registry lookup keys for a characteristic enum value."""
        class_name = enum_member.value.replace(" ", "") + "Characteristic"
        variants = NameVariantGenerator.generate_characteristic_variants(class_name, enum_member.value)
        slug = cls.slugify_characteristic_identifier(enum_member.value)
        org_identifier = f"org.bluetooth.characteristic.{slug}"
        return [*variants, enum_member.name.replace("_", " "), org_identifier]

    @classmethod
    def build_uuid_to_enum_map(cls) -> dict[str, CharacteristicName]:
        """Create a mapping from normalized UUID string to CharacteristicName."""
        uuid_to_enum: dict[str, CharacteristicName] = {}

        for enum_member in CharacteristicName:
            for candidate in cls.generate_candidate_keys(enum_member):
                info = uuid_registry.get_characteristic_info(candidate)
                if info is None:
                    continue
                uuid_to_enum[info.uuid.normalized] = enum_member
                break

        for info_name, enum_member in cls._SPECIAL_INFO_NAME_TO_ENUM.items():
            info = uuid_registry.get_characteristic_info(info_name)
            if info is None:
                continue
            uuid_to_enum.setdefault(info.uuid.normalized, enum_member)

        return uuid_to_enum


def get_characteristic_class_map() -> dict[CharacteristicName, type[BaseCharacteristic[Any]]]:
    """Get the current characteristic class map.

    Backward compatibility function that returns the current registry state.

    Returns:
        Dictionary mapping CharacteristicName enum to characteristic classes
    """
    return CharacteristicRegistry.get_instance()._get_enum_map()  # pylint: disable=protected-access


class CharacteristicRegistry(BaseUUIDClassRegistry[CharacteristicName, BaseCharacteristic[Any]]):
    """Encapsulates all GATT characteristic registry operations."""

    _MODULE_EXCLUSIONS: ClassVar[set[str]] = {"__main__", "__init__", "base", "registry", "templates"}
    _NON_ALPHANUMERIC_RE: ClassVar[re.Pattern[str]] = re.compile(r"[^a-z0-9]+")

    def _get_base_class(self) -> type[BaseCharacteristic[Any]]:
        """Return the base class for characteristic validation."""
        return BaseCharacteristic

    def _discover_sig_classes(self) -> list[type[BaseCharacteristic[Any]]]:
        """Discover all SIG-defined characteristic classes in the package."""
        package_name = __package__ or "bluetooth_sig.gatt.characteristics"
        module_names = ModuleDiscovery.iter_module_names(package_name, self._MODULE_EXCLUSIONS)

        return ModuleDiscovery.discover_classes(
            module_names,
            BaseCharacteristic,
            _is_characteristic_subclass,
        )

    def _build_uuid_to_enum_map(self) -> dict[str, CharacteristicName]:
        """Create a mapping from normalized UUID string to CharacteristicName."""
        uuid_to_enum: dict[str, CharacteristicName] = {}

        for enum_member in CharacteristicName:
            for candidate in _RegistryKeyBuilder.generate_candidate_keys(enum_member):
                info = uuid_registry.get_characteristic_info(candidate)
                if info is None:
                    continue
                uuid_to_enum[info.uuid.normalized] = enum_member
                break

        # Handle special cases (CO2, etc.) - access via static method to avoid protected access
        special_cases = {
            "CO\\textsubscript{2} Concentration": CharacteristicName.CO2_CONCENTRATION,
        }
        for info_name, enum_member in special_cases.items():
            info = uuid_registry.get_characteristic_info(info_name)
            if info is None:
                continue
            uuid_to_enum.setdefault(info.uuid.normalized, enum_member)

        return uuid_to_enum

    def _build_enum_map(self) -> dict[CharacteristicName, type[BaseCharacteristic[Any]]]:
        """Build the enum → class mapping using runtime discovery."""
        mapping: dict[CharacteristicName, type[BaseCharacteristic[Any]]] = {}
        uuid_to_enum = self._build_uuid_to_enum_map()

        for char_cls in self._discover_sig_classes():
            try:
                uuid_obj = char_cls.get_class_uuid()
            except (AttributeError, ValueError):
                continue

            if uuid_obj is None:
                continue

            enum_member = uuid_to_enum.get(uuid_obj.normalized)
            if enum_member is None:
                continue

            existing = mapping.get(enum_member)
            if existing is not None and existing is not char_cls:
                raise RuntimeError(
                    f"Multiple characteristic classes resolved for {enum_member.name}: "
                    f"{existing.__name__} and {char_cls.__name__}"
                )

            mapping[enum_member] = char_cls

        return mapping

    def _load(self) -> None:
        """Perform the actual loading of registry data."""
        # Trigger cache building
        _ = self._get_enum_map()
        _ = self._get_sig_classes_map()
        self._loaded = True

    # Backward compatibility aliases for existing API

    @classmethod
    def register_characteristic_class(
        cls, uuid: str | BluetoothUUID | int, char_cls: type[BaseCharacteristic[Any]], override: bool = False
    ) -> None:
        """Register a custom characteristic class at runtime.

        Backward compatibility wrapper for register_class().
        """
        instance = cls.get_instance()
        instance.register_class(uuid, char_cls, override)

    @classmethod
    def unregister_characteristic_class(cls, uuid: str | BluetoothUUID | int) -> None:
        """Unregister a custom characteristic class.

        Backward compatibility wrapper for unregister_class().
        """
        instance = cls.get_instance()
        instance.unregister_class(uuid)

    @classmethod
    def get_characteristic_class(cls, name: CharacteristicName) -> type[BaseCharacteristic[Any]] | None:
        """Get the characteristic class for a given CharacteristicName enum.

        Backward compatibility wrapper for get_class_by_enum().
        """
        instance = cls.get_instance()
        return instance.get_class_by_enum(name)

    @classmethod
    def get_characteristic_class_by_uuid(cls, uuid: str | BluetoothUUID | int) -> type[BaseCharacteristic[Any]] | None:
        """Get the characteristic class for a given UUID.

        Backward compatibility wrapper for get_class_by_uuid().
        """
        instance = cls.get_instance()
        return instance.get_class_by_uuid(uuid)

    @classmethod
    def get_characteristic(cls, uuid: str | BluetoothUUID | int) -> BaseCharacteristic[Any] | None:
        """Get a characteristic instance from a UUID.

        Args:
            uuid: The characteristic UUID (string, BluetoothUUID, or int)

        Returns:
            Characteristic instance if found, None if UUID not registered

        Raises:
            ValueError: If uuid format is invalid
        """
        # Normalize to BluetoothUUID (let ValueError propagate for invalid format)
        uuid_obj = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)

        instance = cls.get_instance()
        char_cls = instance.get_class_by_uuid(uuid_obj)
        if char_cls is None:
            return None

        return char_cls()

    @staticmethod
    def list_all_characteristic_names() -> list[str]:
        """List all supported characteristic names as strings."""
        return [e.value for e in CharacteristicName]

    @staticmethod
    def list_all_characteristic_enums() -> list[CharacteristicName]:
        """List all supported characteristic names as enum values."""
        return list(CharacteristicName)

    @classmethod
    def get_all_characteristics(cls) -> dict[CharacteristicName, type[BaseCharacteristic[Any]]]:
        """Get all registered characteristic classes."""
        instance = cls.get_instance()
        return instance._get_enum_map().copy()  # pylint: disable=protected-access

    @classmethod
    def clear_custom_registrations(cls) -> None:
        """Clear all custom characteristic registrations (for testing)."""
        instance = cls.get_instance()
        for uuid in list(instance.list_custom_uuids()):
            instance.unregister_class(uuid)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the characteristic class map cache (for testing)."""
        instance = cls.get_instance()
        instance.clear_enum_map_cache()
        instance._load()  # Reload to repopulate  # pylint: disable=protected-access
