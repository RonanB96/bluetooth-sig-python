"""Service Discovery Attribute ID Registry for SDP attribute identifiers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.profile_types import (
    AttributeIdEntry,
    ProtocolParameterEntry,
)


class ServiceDiscoveryAttributeRegistry(
    BaseGenericRegistry["ServiceDiscoveryAttributeRegistry"],
):
    """Registry for SDP attribute identifiers with lazy loading.

    Loads attribute IDs from ``service_discovery/attribute_ids/*.yaml``,
    ``attribute_id_offsets_for_strings.yaml``, and ``protocol_parameters.yaml``.

    Thread-safe: Multiple threads can safely access the registry concurrently.
    """

    def __init__(self) -> None:
        """Initialise the service discovery attribute registry."""
        super().__init__()
        self._attribute_ids: dict[str, list[AttributeIdEntry]] = {}
        self._protocol_parameters: list[ProtocolParameterEntry] = []

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_hex_value(raw: object) -> int | None:
        """Parse a hex string like ``'0x0001'`` into an int."""
        if isinstance(raw, int):
            return raw
        if isinstance(raw, str):
            try:
                return int(raw, 16) if raw.startswith("0x") else int(raw)
            except ValueError:
                return None
        return None

    def _load_attribute_ids_file(self, yaml_path: Path, category: str) -> None:
        """Load a single attribute_ids YAML file into *_attribute_ids[category]*."""
        if not yaml_path.exists():
            return

        with yaml_path.open("r", encoding="utf-8") as fh:
            data = msgspec.yaml.decode(fh.read())

        if not isinstance(data, dict):
            return

        data_dict = cast("dict[str, Any]", data)
        entries_raw = data_dict.get("attribute_ids")
        if not isinstance(entries_raw, list):
            return

        entries: list[AttributeIdEntry] = []
        for entry in entries_raw:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name")
            value = self._parse_hex_value(entry.get("value"))
            if name and value is not None:
                entries.append(AttributeIdEntry(name=str(name), value=value))

        if entries:
            self._attribute_ids[category] = entries

    def _load_protocol_parameters(self, yaml_path: Path) -> None:
        """Load ``protocol_parameters.yaml``."""
        if not yaml_path.exists():
            return

        with yaml_path.open("r", encoding="utf-8") as fh:
            data = msgspec.yaml.decode(fh.read())

        if not isinstance(data, dict):
            return

        data_dict = cast("dict[str, Any]", data)
        params_raw = data_dict.get("protocol_parameters")
        if not isinstance(params_raw, list):
            return

        for entry in params_raw:
            if not isinstance(entry, dict):
                continue
            protocol = entry.get("protocol")
            name = entry.get("name")
            index = entry.get("index")
            if protocol and name and isinstance(index, int):
                self._protocol_parameters.append(
                    ProtocolParameterEntry(
                        protocol=str(protocol),
                        name=str(name),
                        index=index,
                    ),
                )

    def _load(self) -> None:
        """Perform the actual loading of all service discovery data."""
        uuids_path = find_bluetooth_sig_path()
        if not uuids_path:
            self._loaded = True
            return

        sd_path = uuids_path.parent / "service_discovery"
        if not sd_path.exists():
            self._loaded = True
            return

        # Load attribute_ids/*.yaml
        attr_dir = sd_path / "attribute_ids"
        if attr_dir.is_dir():
            for yaml_file in sorted(attr_dir.glob("*.yaml")):
                category = yaml_file.stem
                self._load_attribute_ids_file(yaml_file, category)

        # Load attribute_id_offsets_for_strings.yaml (same schema)
        offsets_file = sd_path / "attribute_id_offsets_for_strings.yaml"
        self._load_attribute_ids_file(offsets_file, "attribute_id_offsets_for_strings")

        # Load protocol_parameters.yaml
        self._load_protocol_parameters(sd_path / "protocol_parameters.yaml")

        self._loaded = True

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_attribute_ids(self, category: str) -> list[AttributeIdEntry]:
        """Get attribute ID entries for a named category.

        Args:
            category: The file stem / category name, e.g. ``"universal_attributes"``,
                ``"a2dp"``, ``"sdp"``, ``"attribute_id_offsets_for_strings"``.

        Returns:
            List of :class:`AttributeIdEntry` or an empty list if not found.
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._attribute_ids.get(category, []))

    def get_all_categories(self) -> list[str]:
        """Return all loaded category names (sorted)."""
        self._ensure_loaded()
        with self._lock:
            return sorted(self._attribute_ids)

    def get_protocol_parameters(self) -> list[ProtocolParameterEntry]:
        """Return all protocol parameter entries."""
        self._ensure_loaded()
        with self._lock:
            return list(self._protocol_parameters)

    def resolve_attribute_name(self, category: str, value: int) -> str | None:
        """Look up the attribute name for a given numeric value within a category.

        Args:
            category: Category name (e.g. ``"universal_attributes"``).
            value: The numeric attribute ID.

        Returns:
            The attribute name or ``None`` if not found.
        """
        self._ensure_loaded()
        with self._lock:
            for entry in self._attribute_ids.get(category, []):
                if entry.value == value:
                    return entry.name
            return None


# Singleton instance for global use
service_discovery_attribute_registry = ServiceDiscoveryAttributeRegistry()
