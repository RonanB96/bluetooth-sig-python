"""Base registry class for Bluetooth SIG registries with UUID support."""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from bluetooth_sig.registry.common import BaseUuidInfo, UuidOrigin, generate_basic_aliases
from bluetooth_sig.registry.utils import load_yaml_uuids, normalize_uuid_string
from bluetooth_sig.types.uuid import BluetoothUUID

U = TypeVar("T")


class BaseGenericRegistry(ABC, Generic[T]):
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

    def _lazy_load(self, loaded_check: Callable[[], bool], loader: Callable[[], None]) -> bool:
        """Thread-safe lazy loading helper."""
        if loaded_check():
            return False
        with self._lock:
            if loaded_check():
                return False
            loader()
            return True

    def _ensure_loaded(self) -> None:
        """Ensure the registry is loaded."""
        self._lazy_load(lambda: self._loaded, self._load)

    @abstractmethod
    def _load(self) -> None:
        """Perform the actual loading of registry data."""


U = TypeVar("U", bound=BaseUuidInfo)


class BaseUUIDRegistry(ABC, Generic[U]):
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
        pass

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

    @abstractmethod
    def _create_info_from_yaml(self, uuid_data: dict[str, Any], uuid: BluetoothUUID) -> U:
        """Create info instance from YAML data.

        Subclasses can override to customize info creation.
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
                canonical_key = identifier.normalized
                return self._canonical_store.get(canonical_key)

            # Normalize string identifier
            search_key = str(identifier).strip()

            # Try UUID normalization first
            try:
                bt_uuid = BluetoothUUID(search_key)
                canonical_key = bt_uuid.normalized
                if canonical_key in self._canonical_store:
                    return self._canonical_store[canonical_key]
            except ValueError:
                pass

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
            if (
                canonical_key in self._canonical_store
                and getattr(self._canonical_store[canonical_key], "origin", None) == UuidOrigin.BLUETOOTH_SIG
            ):
                self._runtime_overrides[canonical_key] = self._canonical_store[canonical_key]

            # Create runtime info
            info = self._create_runtime_info(entry, bt_uuid)
            self._store_info(info)

    @abstractmethod
    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> U:
        """Create runtime info from entry."""

    def remove_runtime_override(self, normalized_uuid: str) -> None:
        """Remove runtime override, restoring original SIG info if available.

        Args:
            normalized_uuid: Normalized UUID string
        """
        self._ensure_loaded()
        with self._lock:
            # Restore original SIG info if we have it
            if normalized_uuid in self._runtime_overrides:
                original_info = self._runtime_overrides.pop(normalized_uuid)
                self._store_info(original_info)
            elif normalized_uuid in self._canonical_store:
                # Remove runtime entry entirely
                info = self._canonical_store[normalized_uuid]
                if getattr(info, "origin", None) == UuidOrigin.RUNTIME:
                    del self._canonical_store[normalized_uuid]
                    # Remove associated aliases
                    aliases_to_remove = [alias for alias, key in self._alias_index.items() if key == normalized_uuid]
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
    def get_instance(cls) -> BaseRegistry[U]:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

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
