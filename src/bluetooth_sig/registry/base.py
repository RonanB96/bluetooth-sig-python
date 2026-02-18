"""Base registry class for Bluetooth SIG registries with UUID support."""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

from bluetooth_sig.registry.utils import (
    find_bluetooth_sig_path,
    load_yaml_uuids,
    normalize_uuid_string,
)
from bluetooth_sig.types.registry import BaseUuidInfo, generate_basic_aliases
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)

T = TypeVar("T")
E = TypeVar("E", bound=Enum)  # For enum-keyed registries
C = TypeVar("C")  # For class types


class RegistryMixin:
    """Mixin providing common registry patterns for singleton, thread safety, and lazy loading.

    This mixin contains shared functionality used by both info-based and class-based registries.
    """

    _lock: threading.RLock
    _loaded: bool

    def _lazy_load(self, loaded_check: Callable[[], bool], loader: Callable[[], None]) -> bool:
        """Thread-safe lazy loading helper using double-checked locking pattern.

        Args:
            loaded_check: Callable that returns True if data is already loaded
            loader: Callable that performs the actual loading

        Returns:
            True if loading was performed, False if already loaded
        """
        if loaded_check():
            return False

        with self._lock:
            # Double-check after acquiring lock for thread safety
            if loaded_check():
                return False

            loader()
            return True

    def _ensure_loaded(self) -> None:
        """Ensure the registry is loaded (thread-safe lazy loading).

        This is a standard implementation that subclasses can use.
        It calls _lazy_load with self._loaded check and self._load as the loader.
        Subclasses that need custom behaviour can override this method.
        """
        self._lazy_load(lambda: self._loaded, self._load)

    @abstractmethod
    def _load(self) -> None:
        """Perform the actual loading of registry data."""


class BaseGenericRegistry(RegistryMixin, ABC, Generic[T]):
    """Base class for generic Bluetooth SIG registries with singleton pattern and thread safety.

    For registries that are not UUID-based.
    """

    _instance: BaseGenericRegistry[T] | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry."""
        self._lock = threading.RLock()
        self._loaded: bool = False

    @classmethod
    def get_instance(cls) -> BaseGenericRegistry[T]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


U = TypeVar("U", bound=BaseUuidInfo)


class BaseUUIDRegistry(RegistryMixin, ABC, Generic[U]):
    """Base class for Bluetooth SIG registries with singleton pattern, thread safety, and UUID support.

    Provides canonical storage, alias indices, and extensible hooks for UUID-based registries.

    Subclasses should:
    1. Call super().__init__() in their __init__ (base class sets self._loaded = False)
    2. Implement _load() to perform actual data loading (must set self._loaded = True when done)
    3. Optionally override _load_yaml_path() to return the YAML file path relative to bluetooth_sig/
    4. Optionally override _generate_aliases(info) for domain-specific alias heuristics
    5. Optionally override _post_store(info) for enrichment (e.g., unit mappings)
    6. Call _ensure_loaded() before accessing data (provided by base class)
    """

    _instance: BaseUUIDRegistry[U] | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the registry."""
        self._lock = threading.RLock()
        self._loaded: bool = False  # Initialized in base class, accessed by subclasses
        # Performance: Use str keys instead of BluetoothUUID for O(1) dict lookups
        # String hashing is faster and these dicts are accessed frequently
        self._canonical_store: dict[str, U] = {}  # normalized_uuid -> info
        self._alias_index: dict[str, str] = {}  # lowercased_alias -> normalized_uuid
        self._runtime_overrides: dict[str, U] = {}  # normalized_uuid -> original SIG info

    @abstractmethod
    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""

    def _generate_aliases(self, info: U) -> set[str]:
        """Generate alias keys for an info entry.

        Default implementation uses conservative basic aliases.
        Subclasses can override for domain-specific heuristics.
        """
        return generate_basic_aliases(info)

    def _post_store(self, info: U) -> None:
        """Perform post-store enrichment for an info entry.

        Default implementation does nothing.
        Subclasses can override for enrichment (e.g., cross-references).
        """

    def _store_info(self, info: U) -> None:
        """Store info with canonical key and generate aliases."""
        canonical_key = info.uuid.normalized

        # Store in canonical location
        self._canonical_store[canonical_key] = info

        # Generate and store aliases
        aliases = self._generate_aliases(info)
        for alias in aliases:
            self._alias_index[alias.lower()] = canonical_key

        # Perform any post-store enrichment
        self._post_store(info)

    def _load_from_yaml(self, yaml_path: Path) -> None:
        """Load UUIDs from YAML file and store them."""
        for uuid_data in load_yaml_uuids(yaml_path):
            uuid_str = normalize_uuid_string(uuid_data["uuid"])
            bt_uuid = BluetoothUUID(uuid_str)

            # Create info with available fields, defaults for missing
            info = self._create_info_from_yaml(uuid_data, bt_uuid)
            self._store_info(info)

    def _load(self) -> None:
        """Perform the actual loading of registry data from YAML.

        Default implementation loads from the path returned by _load_yaml_path().
        Subclasses can override for custom loading behaviour.
        """
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    @abstractmethod
    def _create_info_from_yaml(self, uuid_data: dict[str, Any], uuid: BluetoothUUID) -> U:
        """Create info instance from YAML data.

        Subclasses must implement to create the appropriate info type.
        """

    def get_info(self, identifier: str | BluetoothUUID) -> U | None:
        """Get info by UUID, name, ID, or alias.

        Args:
            identifier: UUID string/int/BluetoothUUID, or name/ID/alias

        Returns:
            Info if found, None otherwise
        """
        self._ensure_loaded()
        with self._lock:
            # Handle BluetoothUUID directly
            if isinstance(identifier, BluetoothUUID):
                canonical_key = identifier.full_form
                return self._canonical_store.get(canonical_key)

            # Normalize string identifier
            search_key = str(identifier).strip()

            # Try UUID normalization first
            try:
                bt_uuid = BluetoothUUID(search_key)
                canonical_key = bt_uuid.full_form
                if canonical_key in self._canonical_store:
                    return self._canonical_store[canonical_key]
            except ValueError:
                logger.warning("UUID normalization failed for registry lookup: %s", search_key)

            # Check alias index (normalized to lowercase)
            alias_key = self._alias_index.get(search_key.lower())
            if alias_key and alias_key in self._canonical_store:
                return self._canonical_store[alias_key]

            return None

    def register_runtime_entry(self, entry: object) -> None:
        """Register a runtime UUID entry, preserving original SIG info if overridden.

        Args:
            entry: Custom entry with uuid, name, id, etc.
        """
        self._ensure_loaded()
        with self._lock:
            bt_uuid = getattr(entry, "uuid", None)
            if bt_uuid is None:
                raise ValueError("Entry must have a uuid attribute")
            bt_uuid = bt_uuid if isinstance(bt_uuid, BluetoothUUID) else BluetoothUUID(bt_uuid)
            canonical_key = bt_uuid.normalized

            # Preserve original SIG info if we're overriding it
            # Assume entries in canonical_store that aren't in runtime_overrides are SIG entries
            if canonical_key in self._canonical_store and canonical_key not in self._runtime_overrides:
                self._runtime_overrides[canonical_key] = self._canonical_store[canonical_key]

            # Create runtime info
            info = self._create_runtime_info(entry, bt_uuid)
            self._store_info(info)

    @abstractmethod
    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> U:
        """Create runtime info from entry."""

    def remove_runtime_override(self, normalized_uuid: BluetoothUUID) -> None:
        """Remove runtime override, restoring original SIG info if available.

        Args:
            normalized_uuid: UUID to remove override for
        """
        self._ensure_loaded()
        with self._lock:
            # Restore original SIG info if we have it
            uuid_key = normalized_uuid.full_form
            if uuid_key in self._runtime_overrides:
                original_info = self._runtime_overrides.pop(uuid_key)
                self._store_info(original_info)
            elif uuid_key in self._canonical_store:
                # Remove runtime entry entirely
                # NOTE: Runtime tracking is registry-specific (e.g., uuid_registry uses _runtime_uuids set)
                del self._canonical_store[uuid_key]
                # Remove associated aliases
                aliases_to_remove = [alias for alias, key in self._alias_index.items() if key == uuid_key]
                for alias in aliases_to_remove:
                    del self._alias_index[alias]

    def list_registered(self) -> list[str]:
        """List all registered normalized UUIDs."""
        self._ensure_loaded()
        with self._lock:
            return list(self._canonical_store.keys())

    def list_aliases(self, uuid: BluetoothUUID) -> list[str]:
        """List all aliases for a normalized UUID."""
        self._ensure_loaded()
        with self._lock:
            return [alias for alias, key in self._alias_index.items() if key == uuid.normalized]

    @classmethod
    def get_instance(cls) -> BaseUUIDRegistry[U]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


class BaseUUIDClassRegistry(RegistryMixin, ABC, Generic[E, C]):
    """Base class for UUID-based registries that store classes with enum-keyed access.

    This registry type is designed for GATT characteristics and services that need:
    1. UUID → Class mapping (e.g., "2A19" → BatteryLevelCharacteristic class)
    2. Enum → Class mapping (e.g., CharacteristicName.BATTERY_LEVEL → BatteryLevelCharacteristic class)
    3. Runtime class registration with override protection
    4. Thread-safe singleton pattern with lazy loading

    Unlike BaseUUIDRegistry which stores info objects (metadata), this stores actual classes
    that can be instantiated.

    Subclasses should:
    1. Call super().__init__() in their __init__
    2. Implement _load() to perform class discovery (must set self._loaded = True)
    3. Implement _build_enum_map() to create the enum → class mapping
    4. Implement _discover_sig_classes() to find built-in SIG classes
    5. Optionally override _allows_sig_override() for custom override rules
    """

    _instance: BaseUUIDClassRegistry[E, C] | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the class registry."""
        self._lock = threading.RLock()
        self._loaded: bool = False
        self._custom_classes: dict[BluetoothUUID, type[C]] = {}
        self._sig_class_cache: dict[BluetoothUUID, type[C]] | None = None
        self._enum_map_cache: dict[E, type[C]] | None = None

    @abstractmethod
    def _get_base_class(self) -> type[C]:
        """Return the base class that all registered classes must inherit from.

        This is used for validation when registering custom classes.

        Returns:
            The base class type
        """

    @abstractmethod
    def _build_enum_map(self) -> dict[E, type[C]]:
        """Build the enum → class mapping.

        This should discover all SIG-defined classes and map them to their enum values.

        Returns:
            Dictionary mapping enum members to class types
        """

    @abstractmethod
    def _discover_sig_classes(self) -> list[type[C]]:
        """Discover all SIG-defined classes in the package.

        Returns:
            List of discovered class types
        """

    def _allows_sig_override(self, custom_cls: type[C], sig_cls: type[C]) -> bool:
        """Check if a custom class is allowed to override a SIG class.

        Default implementation checks for _allows_sig_override attribute on the custom class.
        Subclasses can override for custom logic.

        Args:
            custom_cls: The custom class attempting to override
            sig_cls: The existing SIG class being overridden (unused in default implementation)

        Returns:
            True if override is allowed, False otherwise
        """
        del sig_cls  # Unused in default implementation
        return getattr(custom_cls, "_allows_sig_override", False)

    def _get_enum_map(self) -> dict[E, type[C]]:
        """Get the cached enum → class mapping, building if necessary."""
        if self._enum_map_cache is None:
            self._enum_map_cache = self._build_enum_map()
        return self._enum_map_cache

    def _get_sig_classes_map(self) -> dict[BluetoothUUID, type[C]]:
        """Get the cached UUID → SIG class mapping, building if necessary."""
        if self._sig_class_cache is None:
            self._sig_class_cache = {}
            for cls in self._discover_sig_classes():
                try:
                    uuid_obj = cls.get_class_uuid()  # type: ignore[attr-defined]  # Generic C bound lacks this method; runtime dispatch is correct
                    if uuid_obj:
                        self._sig_class_cache[uuid_obj] = cls
                except (AttributeError, ValueError):
                    # Skip classes that can't resolve UUID
                    continue
        return self._sig_class_cache

    def register_class(self, uuid: str | BluetoothUUID | int, cls: type[C], override: bool = False) -> None:
        """Register a custom class at runtime.

        Args:
            uuid: The UUID for this class (string, BluetoothUUID, or int)
            cls: The class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls is not the correct type
            ValueError: If UUID conflicts with existing registration and override=False,
                       or if attempting to override SIG class without permission
        """
        self._ensure_loaded()

        # Validate that cls is actually a subclass of the base class
        base_class = self._get_base_class()
        if not issubclass(cls, base_class):
            raise TypeError(f"Registered class must inherit from {base_class.__name__}, got {cls.__name__}")

        # Normalize to BluetoothUUID
        bt_uuid = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)

        # Check for SIG class collision
        sig_classes = self._get_sig_classes_map()
        sig_cls = sig_classes.get(bt_uuid)

        with self._lock:
            # Check for custom class collision
            if not override and bt_uuid in self._custom_classes:
                raise ValueError(f"UUID {bt_uuid} already registered. Use override=True to replace.")

            # If collides with SIG class, enforce override rules
            if sig_cls is not None:
                if not override:
                    raise ValueError(
                        f"UUID {bt_uuid} conflicts with existing SIG class {sig_cls.__name__}. "
                        "Use override=True to replace."
                    )
                if not self._allows_sig_override(cls, sig_cls):
                    raise ValueError(
                        f"Override of SIG class {sig_cls.__name__} requires "
                        f"_allows_sig_override=True on {cls.__name__}."
                    )

            self._custom_classes[bt_uuid] = cls

    def unregister_class(self, uuid: str | BluetoothUUID | int) -> None:
        """Unregister a custom class.

        Args:
            uuid: The UUID to unregister (string, BluetoothUUID, or int)
        """
        bt_uuid = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)
        with self._lock:
            self._custom_classes.pop(bt_uuid, None)

    def get_class_by_uuid(self, uuid: str | BluetoothUUID | int) -> type[C] | None:
        """Get the class for a given UUID.

        Checks custom classes first, then SIG classes.

        Args:
            uuid: The UUID to look up (string, BluetoothUUID, or int)

        Returns:
            The class if found, None otherwise
        """
        self._ensure_loaded()

        # Normalize to BluetoothUUID
        bt_uuid = uuid if isinstance(uuid, BluetoothUUID) else BluetoothUUID(uuid)

        # Check custom classes first
        with self._lock:
            if custom_cls := self._custom_classes.get(bt_uuid):
                return custom_cls

        # Check SIG classes
        return self._get_sig_classes_map().get(bt_uuid)

    def get_class_by_enum(self, enum_member: E) -> type[C] | None:
        """Get the class for a given enum member.

        Args:
            enum_member: The enum member to look up

        Returns:
            The class if found, None otherwise
        """
        self._ensure_loaded()
        return self._get_enum_map().get(enum_member)

    def list_custom_uuids(self) -> list[BluetoothUUID]:
        """List all custom registered UUIDs.

        Returns:
            List of UUIDs with custom class registrations
        """
        with self._lock:
            return list(self._custom_classes.keys())

    def clear_enum_map_cache(self) -> None:
        """Clear the cached enum → class mapping.

        Useful when classes are registered/unregistered at runtime.
        """
        self._enum_map_cache = None
        self._sig_class_cache = None

    @classmethod
    def get_instance(cls) -> BaseUUIDClassRegistry[E, C]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
