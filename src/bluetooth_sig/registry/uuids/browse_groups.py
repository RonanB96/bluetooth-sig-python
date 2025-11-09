"""Browse group identifiers registry for Bluetooth SIG browse group identifiers."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class BrowseGroupInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG browse group identifier."""

    uuid: BluetoothUUID
    name: str
    id: str


class BrowseGroupsRegistry(BaseRegistry[BrowseGroupInfo]):
    """Registry for Bluetooth SIG browse group identifiers."""

    def __init__(self) -> None:
        """Initialize the browse groups registry."""
        super().__init__()
        self._browse_groups: dict[str, BrowseGroupInfo] = {}
        self._name_to_info: dict[str, BrowseGroupInfo] = {}
        self._id_to_info: dict[str, BrowseGroupInfo] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Ensure the registry is loaded (thread-safe lazy loading)."""
        if self._loaded:
            return
        
        with self._lock:
            if self._loaded:
                return
            
            base_path = find_bluetooth_sig_path()
            if not base_path:
                self._loaded = True
                return

            # Load browse group UUIDs
            browse_groups_yaml = base_path / "uuids" / "browse_group_identifiers.yaml"
            if browse_groups_yaml.exists():
                for item in load_yaml_uuids(browse_groups_yaml):
                    try:
                        uuid = parse_bluetooth_uuid(item["uuid"])
                        name = item["name"]
                        browse_group_id = item["id"]

                        info = BrowseGroupInfo(uuid=uuid, name=name, id=browse_group_id)

                        # Store by UUID string for fast lookup
                        self._browse_groups[uuid.short_form.upper()] = info
                        self._name_to_info[name.lower()] = info
                        self._id_to_info[browse_group_id] = info

                    except (KeyError, ValueError):
                        # Skip malformed entries
                        continue
            self._loaded = True

    def get_browse_group_info(self, uuid: str | int | BluetoothUUID) -> BrowseGroupInfo | None:
        """Get browse group information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        self._ensure_loaded()
        try:
            bt_uuid = parse_bluetooth_uuid(uuid)
            return self._browse_groups.get(bt_uuid.short_form.upper())
        except ValueError:
            return None

    def get_browse_group_info_by_name(self, name: str) -> BrowseGroupInfo | None:
        """Get browse group information by name (case insensitive).

        Args:
            name: The browse group name to look up

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        self._ensure_loaded()
        return self._name_to_info.get(name.lower())

    def get_browse_group_info_by_id(self, browse_group_id: str) -> BrowseGroupInfo | None:
        """Get browse group information by browse group ID.

        Args:
            browse_group_id: The browse group ID to look up

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        self._ensure_loaded()
        return self._id_to_info.get(browse_group_id)

    def is_browse_group_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known browse group.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known browse group, False otherwise
        """
        self._ensure_loaded()
        return self.get_browse_group_info(uuid) is not None

    def get_all_browse_groups(self) -> list[BrowseGroupInfo]:
        """Get all browse groups in the registry.

        Returns:
            List of all BrowseGroupInfo objects
        """
        self._ensure_loaded()
        return list(self._browse_groups.values())


# Global instance for convenience
browse_groups_registry = BrowseGroupsRegistry.get_instance()
