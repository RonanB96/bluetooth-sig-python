"""Bluetooth SIG GATT characteristic registry.

This module contains the characteristic registry implementation and
class mappings. CharacteristicName enum is now centralized in
types.gatt_enums to avoid circular imports.
"""

from __future__ import annotations

import inspect
import pkgutil
import re
import threading
from functools import lru_cache
from importlib import import_module

from typing_extensions import TypeGuard

from ...types.gatt_enums import CharacteristicName
from ...types.uuid import BluetoothUUID
from ..registry_utils import TypeValidator
from ..resolver import NameVariantGenerator
from ..uuid_registry import uuid_registry
from .base import BaseCharacteristic

# Export for other modules to import
__all__ = ["CharacteristicName", "CharacteristicRegistry"]


class _CharacteristicClassValidator:  # pylint: disable=too-few-public-methods
    """Utility class for validating characteristic classes.

    Note: Single-purpose validator class - pylint disable justified.
    """

    @staticmethod
    def is_characteristic_subclass(candidate: object) -> TypeGuard[type[BaseCharacteristic]]:
        """Return True when candidate is a BaseCharacteristic subclass."""
        return TypeValidator.is_subclass_of(candidate, BaseCharacteristic)


class _RegistryKeyBuilder:
    """Builds registry lookup keys for characteristics."""

    _NON_ALPHANUMERIC_RE = re.compile(r"[^a-z0-9]+")

    # Special cases for characteristics whose YAML names don't match enum display names
    # NOTE: CO2 uses LaTeX formatting in official Bluetooth SIG spec: "CO\textsubscript{2} Concentration"
    _SPECIAL_INFO_NAME_TO_ENUM = {
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


class _CharacteristicClassDiscovery:
    """Handles discovery and validation of characteristic classes in the package."""

    _MODULE_EXCLUSIONS = {"__main__", "__init__", "base", "registry", "templates"}

    @classmethod
    def iter_module_names(cls) -> list[str]:
        """Return sorted characteristic module names discovered via pkgutil.walk_packages [1]_.

        References:
            .. [1] Python standard library documentation, pkgutil.walk_packages,
               https://docs.python.org/3/library/pkgutil.html#pkgutil.walk_packages
        """
        package_name = __package__ or "bluetooth_sig.gatt.characteristics"
        package = import_module(package_name)
        module_names: list[str] = []
        prefix = f"{package_name}."
        for module_info in pkgutil.walk_packages(package.__path__, prefix):
            module_basename = module_info.name.rsplit(".", 1)[-1]
            if module_basename in cls._MODULE_EXCLUSIONS:
                continue
            module_names.append(module_info.name)
        module_names.sort()
        return module_names

    @classmethod
    def discover_classes(cls) -> list[type[BaseCharacteristic]]:
        """Discover all concrete characteristic classes defined in the package.

        Validates that discovered classes have required methods for proper operation.
        """
        discovered: list[type[BaseCharacteristic]] = []
        for module_name in cls.iter_module_names():
            module = import_module(module_name)
            candidates: list[type[BaseCharacteristic]] = []
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not _CharacteristicClassValidator.is_characteristic_subclass(obj):
                    continue
                if obj is BaseCharacteristic or getattr(obj, "_is_template", False):
                    continue
                if obj.__module__ != module.__name__:
                    continue

                # Validate that the class has required methods
                if not hasattr(obj, "get_class_uuid") or not callable(obj.get_class_uuid):
                    continue  # Skip classes without proper UUID resolution

                candidates.append(obj)
            candidates.sort(key=lambda cls: cls.__name__)
            discovered.extend(candidates)
        return discovered


class _CharacteristicMapBuilder:
    """Builds and caches the characteristic class map."""

    @staticmethod
    def build_map() -> dict[CharacteristicName, type[BaseCharacteristic]]:
        """Build the characteristic class mapping lazily using runtime discovery."""
        mapping: dict[CharacteristicName, type[BaseCharacteristic]] = {}
        uuid_to_enum = _RegistryKeyBuilder.build_uuid_to_enum_map()

        for char_cls in _CharacteristicClassDiscovery.discover_classes():
            uuid_obj = char_cls.get_class_uuid()
            if uuid_obj is None:
                continue
            enum_member = uuid_to_enum.get(uuid_obj.normalized)
            if enum_member is None:
                continue
            existing = mapping.get(enum_member)
            if existing is not None and existing is not char_cls:
                raise RuntimeError(
                    f"Multiple characteristic classes resolved for {enum_member.name}:"
                    f" {existing.__name__} and {char_cls.__name__}"
                )
            mapping[enum_member] = char_cls

        return mapping

    @staticmethod
    @lru_cache(maxsize=1)
    def get_cached_map() -> dict[CharacteristicName, type[BaseCharacteristic]]:
        """Return the cached characteristic class map."""
        return _CharacteristicMapBuilder.build_map()

    @staticmethod
    def clear_cache() -> None:
        """Clear the characteristic class map cache."""
        _CharacteristicMapBuilder.get_cached_map.cache_clear()


# Public API - enum-keyed map
CHARACTERISTIC_CLASS_MAP = _CharacteristicMapBuilder.get_cached_map()


class CharacteristicRegistry:
    """Encapsulates all GATT characteristic registry operations."""

    _lock = threading.RLock()
    _custom_characteristic_classes: dict[BluetoothUUID, type[BaseCharacteristic]] = {}

    @classmethod
    def register_characteristic_class(cls, uuid: str | BluetoothUUID, char_cls: object, override: bool = False) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID)
            char_cls: The characteristic class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If char_cls does not inherit from BaseCharacteristic
            ValueError: If UUID conflicts with existing registration and override=False
        """
        # Runtime safety check retained in case of dynamic caller misuse despite type hints.
        if not _CharacteristicClassValidator.is_characteristic_subclass(char_cls):
            raise TypeError(f"Class {char_cls!r} must inherit from BaseCharacteristic")

        characteristic_cls: type[BaseCharacteristic] = char_cls

        # Always normalize UUID to BluetoothUUID
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid

        # Determine if this UUID is already represented by a SIG (built-in) characteristic
        def _find_sig_class_for_uuid(target: BluetoothUUID) -> type[BaseCharacteristic] | None:
            for candidate in _CharacteristicMapBuilder.get_cached_map().values():
                resolved_uuid_obj = candidate.get_class_uuid()
                if resolved_uuid_obj and resolved_uuid_obj == target:
                    return candidate
            return None

        sig_cls = _find_sig_class_for_uuid(bt_uuid)

        with cls._lock:
            # Prevent duplicate custom registration unless override explicitly requested
            if not override and bt_uuid in cls._custom_characteristic_classes:
                raise ValueError(f"UUID {bt_uuid} already registered. Use override=True to replace.")

            # If collides with a SIG characteristic, enforce explicit override + permission flag
            if sig_cls is not None:
                if not override:
                    raise ValueError(
                        f"UUID {bt_uuid} conflicts with existing SIG characteristic {sig_cls.__name__}. "
                        "Use override=True to replace."
                    )
                # Require an explicit opt‑in marker on the custom class
                allows_override = characteristic_cls.get_allows_sig_override()
                if not allows_override:
                    raise ValueError(
                        "Override of SIG characteristic "
                        f"{sig_cls.__name__} requires _allows_sig_override=True on {characteristic_cls.__name__}."
                    )

            cls._custom_characteristic_classes[bt_uuid] = characteristic_cls

    @classmethod
    def unregister_characteristic_class(cls, uuid: str | BluetoothUUID) -> None:
        """Unregister a custom characteristic class.

        Args:
            uuid: The characteristic UUID to unregister (string or BluetoothUUID)
        """
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        with cls._lock:
            cls._custom_characteristic_classes.pop(bt_uuid, None)

    @staticmethod
    def get_characteristic_class(
        name: CharacteristicName,
    ) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given CharacteristicName enum.

        This API is enum-only. Callers must pass a `CharacteristicName`.
        """
        return _CharacteristicMapBuilder.get_cached_map().get(name)

    @staticmethod
    def list_all_characteristic_names() -> list[str]:
        """List all supported characteristic names as strings.

        Returns:
            List of all characteristic names.
        """
        return [e.value for e in CharacteristicName]

    @staticmethod
    def list_all_characteristic_enums() -> list[CharacteristicName]:
        """List all supported characteristic names as enum values.

        Returns:
            List of all characteristic enum values.
        """
        return list(CharacteristicName)

    @classmethod
    def create_characteristic(
        cls,
        uuid: str | BluetoothUUID,
    ) -> BaseCharacteristic | None:
        """Create a characteristic instance from a UUID.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID).

        Returns:
            Characteristic instance if found, None otherwise.
        """
        # Handle UUID input
        if isinstance(uuid, BluetoothUUID):
            uuid_obj = uuid
        else:
            try:
                uuid_obj = BluetoothUUID(uuid)
            except ValueError:
                # Invalid UUID format, cannot create characteristic
                return None

        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_characteristic_classes.get(uuid_obj):
                return custom_cls()

        # Look up by UUID at class level (no instantiation needed)
        for _, char_cls in _CharacteristicMapBuilder.get_cached_map().items():
            resolved_uuid = char_cls.get_class_uuid()
            if resolved_uuid and resolved_uuid == uuid_obj:
                return char_cls()

        return None

    @classmethod
    def get_characteristic_class_by_uuid(cls, uuid: str | BluetoothUUID) -> type[BaseCharacteristic] | None:
        """Get the characteristic class for a given UUID.

        Args:
            uuid: The characteristic UUID (with or without dashes).

        Returns:
            The characteristic class if found, None otherwise.
        """
        # Always normalize UUID to BluetoothUUID
        try:
            bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        except ValueError:
            return None

        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_characteristic_classes.get(bt_uuid):
                return custom_cls

        # Look up by UUID at class level (no instantiation needed)
        for char_cls in _CharacteristicMapBuilder.get_cached_map().values():
            resolved_uuid = char_cls.get_class_uuid()
            if resolved_uuid and resolved_uuid == bt_uuid:
                return char_cls

        return None

    @staticmethod
    def get_all_characteristics() -> dict[CharacteristicName, type[BaseCharacteristic]]:
        """Get all registered characteristic classes.

        Returns:
            Dictionary mapping characteristic names to classes
        """
        result: dict[CharacteristicName, type[BaseCharacteristic]] = {}
        for name, char_cls in _CharacteristicMapBuilder.get_cached_map().items():
            result[name] = char_cls
        return result

    @classmethod
    def clear_custom_registrations(cls) -> None:
        """Clear all custom characteristic registrations (for testing)."""
        with cls._lock:
            cls._custom_characteristic_classes.clear()

    @staticmethod
    def clear_cache() -> None:
        """Clear the characteristic class map cache (for testing).

        This forces the registry to be rebuilt on next access.
        Use sparingly - primarily for testing scenarios where
        characteristic classes are modified at runtime.
        """
        _CharacteristicMapBuilder.clear_cache()
