"""Browse groups registry for Bluetooth SIG browse group definitions."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.types.registry.browse_group_identifiers import BrowseGroupInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class BrowseGroupsRegistry(BaseUUIDRegistry[BrowseGroupInfo]):
    """Registry for Bluetooth SIG browse group identifiers."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/browse_groups.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> BrowseGroupInfo:
        """Create BrowseGroupInfo from YAML data."""
        return BrowseGroupInfo(
            uuid=uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> BrowseGroupInfo:
        """Create runtime BrowseGroupInfo from entry."""
        return BrowseGroupInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
        )

    def get_browse_group_info(self, uuid: str | BluetoothUUID) -> BrowseGroupInfo | None:
        """Get browse group information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        return self.get_info(uuid)

    def get_browse_group_info_by_name(self, name: str) -> BrowseGroupInfo | None:
        """Get browse group information by name (case insensitive).

        Args:
            name: The browse group name to look up

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        self._ensure_loaded()
        # Use the base class method or implement custom logic
        for info in self._canonical_store.values():
            if info.name.lower() == name.lower():
                return info
        return None

    def get_browse_group_info_by_id(self, browse_group_id: str) -> BrowseGroupInfo | None:
        """Get browse group information by browse group ID.

        Args:
            browse_group_id: The browse group ID to look up

        Returns:
            BrowseGroupInfo if found, None otherwise
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.id == browse_group_id:
                return info
        return None

    def is_browse_group_uuid(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known browse group.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known browse group, False otherwise
        """
        return self.get_info(uuid) is not None

    def get_all_browse_groups(self) -> list[BrowseGroupInfo]:
        """Get all browse groups in the registry.

        Returns:
            List of all BrowseGroupInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance for convenience
browse_groups_registry = BrowseGroupsRegistry.get_instance()
