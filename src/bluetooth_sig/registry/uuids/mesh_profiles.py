"""Mesh profiles registry for Bluetooth SIG mesh profile definitions."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.mesh_profile_uuids import MeshProfileInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class MeshProfilesRegistry(BaseRegistry[MeshProfileInfo]):
    """Registry for Bluetooth SIG mesh profile definitions."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/mesh_profiles.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> MeshProfileInfo:
        """Create MeshProfileInfo from YAML data."""
        return MeshProfileInfo(
            uuid=uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
            summary="",
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> MeshProfileInfo:
        """Create runtime MeshProfileInfo from entry."""
        return MeshProfileInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
            summary=getattr(entry, "summary", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of mesh profiles data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_mesh_profile_info(self, uuid: str | int | BluetoothUUID) -> MeshProfileInfo | None:
        """Get mesh profile information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        return self.get_info(uuid)

    def get_mesh_profile_info_by_name(self, name: str) -> MeshProfileInfo | None:
        """Get mesh profile information by name (case insensitive).

        Args:
            name: The mesh profile name to look up

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.name.lower() == name.lower():
                return info
        return None

    def get_mesh_profile_info_by_id(self, mesh_profile_id: str) -> MeshProfileInfo | None:
        """Get mesh profile information by mesh profile ID.

        Args:
            mesh_profile_id: The mesh profile ID to look up

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.id == mesh_profile_id:
                return info
        return None

    def is_mesh_profile_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known mesh profile.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known mesh profile, False otherwise
        """
        return self.get_info(uuid) is not None

    def get_all_mesh_profiles(self) -> list[MeshProfileInfo]:
        """Get all mesh profiles in the registry.

        Returns:
            List of all MeshProfileInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance for convenience
mesh_profiles_registry = MeshProfilesRegistry.get_instance()
