"""Permitted Characteristics Registry for profile service constraints."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.profile_types import PermittedCharacteristicEntry

# Profile subdirectories that contain ``*_permitted_characteristics.yaml``.
_PROFILE_DIRS: tuple[str, ...] = ("ess", "uds", "imds")


class PermittedCharacteristicsRegistry(
    BaseGenericRegistry["PermittedCharacteristicsRegistry"],
):
    """Registry for profile-specific permitted characteristic lists.

    Loads ``permitted_characteristics`` YAML files from ESS, UDS and IMDS
    profile subdirectories under ``profiles_and_services/``.

    Thread-safe: Multiple threads can safely access the registry concurrently.
    """

    def __init__(self) -> None:
        """Initialise the permitted characteristics registry."""
        super().__init__()
        self._entries: dict[str, list[PermittedCharacteristicEntry]] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_yaml_file(self, yaml_path: Path, profile: str) -> None:
        """Load a single permitted-characteristics YAML file."""
        if not yaml_path.exists():
            return

        with yaml_path.open("r", encoding="utf-8") as fh:
            data = msgspec.yaml.decode(fh.read())

        if not isinstance(data, dict):
            return

        data_dict = cast("dict[str, Any]", data)
        items_raw = data_dict.get("permitted_characteristics")
        if not isinstance(items_raw, list):
            return

        entries: list[PermittedCharacteristicEntry] = []
        for item in items_raw:
            if not isinstance(item, dict):
                continue
            service = item.get("service")
            chars_raw = item.get("characteristics")
            if not isinstance(service, str) or not isinstance(chars_raw, list):
                continue
            characteristics = tuple(str(c) for c in chars_raw if isinstance(c, str))
            if characteristics:
                entries.append(
                    PermittedCharacteristicEntry(
                        service=service,
                        characteristics=characteristics,
                    ),
                )

        if entries:
            self._entries[profile] = entries

    def _load(self) -> None:
        """Load all permitted-characteristics YAML files."""
        uuids_path = find_bluetooth_sig_path()
        if not uuids_path:
            self._loaded = True
            return

        profiles_path = uuids_path.parent / "profiles_and_services"
        if not profiles_path.exists():
            self._loaded = True
            return

        for profile_dir in _PROFILE_DIRS:
            dir_path = profiles_path / profile_dir
            if not dir_path.is_dir():
                continue
            for yaml_file in sorted(dir_path.glob("*_permitted_characteristics.yaml")):
                self._load_yaml_file(yaml_file, profile_dir)

        self._loaded = True

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_permitted_characteristics(self, profile: str) -> list[str]:
        """Get the flat list of permitted characteristic identifiers for a profile.

        Args:
            profile: Profile key (e.g. ``"ess"``, ``"uds"``, ``"imds"``).

        Returns:
            List of characteristic identifier strings, or an empty list.
        """
        self._ensure_loaded()
        with self._lock:
            entries = self._entries.get(profile, [])
            return [c for entry in entries for c in entry.characteristics]

    def get_entries(self, profile: str) -> list[PermittedCharacteristicEntry]:
        """Get the structured permitted-characteristic entries for a profile.

        Args:
            profile: Profile key (e.g. ``"ess"``, ``"uds"``, ``"imds"``).

        Returns:
            List of :class:`PermittedCharacteristicEntry` or an empty list.
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._entries.get(profile, []))

    def get_all_profiles(self) -> list[str]:
        """Return all loaded profile keys (sorted)."""
        self._ensure_loaded()
        with self._lock:
            return sorted(self._entries)


# Singleton instance for global use
permitted_characteristics_registry = PermittedCharacteristicsRegistry()
