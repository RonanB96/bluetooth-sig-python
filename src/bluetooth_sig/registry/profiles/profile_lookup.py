"""Profile Lookup Registry for simple name/value profile parameters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.profile_types import ProfileLookupEntry

# Field names tried (in order) when extracting the integer value from a YAML entry.
_VALUE_FIELDS: tuple[str, ...] = ("value", "id", "identifier", "attribute", "MDEP_data_type")

# Field names tried (in order) when extracting the human-readable name.
_NAME_FIELDS: tuple[str, ...] = (
    "name",
    "label",
    "codec",
    "description",
    "audio_location",
    "mnemonic",
    "client_name",
    "data_type",
    "document_name",
)

# Directories containing LTV / codec-capability structures — deferred.
_DEFERRED_DIRS: frozenset[str] = frozenset(
    {
        "ltv_structures",
        "metadata_ltv",
        "codec_capabilities",
        "codec_configuration_ltv",
    },
)


class ProfileLookupRegistry(BaseGenericRegistry["ProfileLookupRegistry"]):
    """Registry for simple profile parameter lookup tables.

    Loads non-LTV, non-permitted-characteristics YAML files from
    ``profiles_and_services/`` and normalises each entry into a
    :class:`ProfileLookupEntry` keyed by the YAML top-level key.

    Thread-safe: Multiple threads can safely access the registry concurrently.
    """

    def __init__(self) -> None:
        """Initialise the profile lookup registry."""
        super().__init__()
        self._tables: dict[str, list[ProfileLookupEntry]] = {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_int_value(entry: dict[str, Any]) -> int | None:
        """Return the first integer-coercible value from *entry*."""
        for field in _VALUE_FIELDS:
            raw = entry.get(field)
            if raw is None:
                continue
            if isinstance(raw, int):
                return raw
            if isinstance(raw, str):
                try:
                    return int(raw, 16) if raw.startswith("0x") else int(raw)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_name(entry: dict[str, Any]) -> str | None:
        """Return the first usable name string from *entry*."""
        for field in _NAME_FIELDS:
            raw = entry.get(field)
            if isinstance(raw, str) and raw:
                return raw
        return None

    @staticmethod
    def _build_metadata(entry: dict[str, Any], used_keys: set[str]) -> dict[str, str]:
        """Collect remaining string-coercible fields as metadata."""
        meta: dict[str, str] = {}
        for key, val in entry.items():
            if key in used_keys:
                continue
            if isinstance(val, (str, int, float, bool)):
                meta[key] = str(val)
        return meta

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_yaml_file(self, yaml_path: Path) -> None:
        """Load a single YAML file and store entries keyed by top-level key."""
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = msgspec.yaml.decode(fh.read())

        if not isinstance(data, dict):
            return

        data_dict = cast("dict[str, Any]", data)
        for top_key, entries_raw in data_dict.items():
            if not isinstance(entries_raw, list):
                continue

            entries: list[ProfileLookupEntry] = []
            for entry in entries_raw:
                if not isinstance(entry, dict):
                    continue

                value = self._extract_int_value(entry)
                name = self._extract_name(entry)
                if value is None or name is None:
                    continue

                # Determine which keys were consumed for name and value
                used: set[str] = set()
                for field in _VALUE_FIELDS:
                    raw = entry.get(field)
                    if raw is not None:
                        if isinstance(raw, int):
                            used.add(field)
                            break
                        if isinstance(raw, str):
                            try:
                                int(raw, 16) if raw.startswith("0x") else int(raw)
                                used.add(field)
                                break
                            except ValueError:
                                continue
                for field in _NAME_FIELDS:
                    raw = entry.get(field)
                    if isinstance(raw, str) and raw:
                        used.add(field)
                        break

                metadata = self._build_metadata(entry, used)
                entries.append(ProfileLookupEntry(name=name, value=value, metadata=metadata))

            if entries:
                self._tables[top_key] = entries

    @staticmethod
    def _is_deferred(path: Path) -> bool:
        """Return True if *path* is inside a deferred subdirectory."""
        return any(part in _DEFERRED_DIRS for part in path.parts)

    @staticmethod
    def _is_permitted_characteristics(path: Path) -> bool:
        """Return True if *path* is a permitted-characteristics file."""
        return "permitted_characteristics" in path.name

    def _load(self) -> None:
        """Load all non-LTV, non-permitted-characteristics profile YAMLs."""
        uuids_path = find_bluetooth_sig_path()
        if not uuids_path:
            self._loaded = True
            return

        profiles_path = uuids_path.parent / "profiles_and_services"
        if not profiles_path.exists():
            self._loaded = True
            return

        for yaml_file in sorted(profiles_path.rglob("*.yaml")):
            if self._is_deferred(yaml_file) or self._is_permitted_characteristics(yaml_file):
                continue
            self._load_yaml_file(yaml_file)

        self._loaded = True

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_entries(self, table_key: str) -> list[ProfileLookupEntry]:
        """Get all entries for a named lookup table.

        Args:
            table_key: The YAML top-level key, e.g. ``"audio_codec_id"``,
                ``"bearer_technology"``, ``"display_types"``.

        Returns:
            List of :class:`ProfileLookupEntry` or an empty list if not found.
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._tables.get(table_key, []))

    def get_all_table_keys(self) -> list[str]:
        """Return all loaded table key names (sorted)."""
        self._ensure_loaded()
        with self._lock:
            return sorted(self._tables)

    def resolve_name(self, table_key: str, value: int) -> str | None:
        """Look up the name for a given numeric value within a table.

        Args:
            table_key: Table key (e.g. ``"bearer_technology"``).
            value: The numeric identifier.

        Returns:
            The entry name or ``None`` if not found.
        """
        self._ensure_loaded()
        with self._lock:
            for entry in self._tables.get(table_key, []):
                if entry.value == value:
                    return entry.name
            return None


# Singleton instance for global use
profile_lookup_registry = ProfileLookupRegistry()
