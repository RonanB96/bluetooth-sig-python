"""Mesh profiles registry for Bluetooth SIG mesh profile definitions."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class MeshProfileInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG mesh profile."""

    uuid: BluetoothUUID
    name: str
    id: str


class MeshProfilesRegistry(BaseRegistry[MeshProfileInfo]):
    """Registry for Bluetooth SIG mesh profile definitions."""

    def __init__(self) -> None:
        """Initialize the mesh profiles registry."""
        super().__init__()
        self._mesh_profiles: dict[str, MeshProfileInfo] = {}
        self._name_to_info: dict[str, MeshProfileInfo] = {}
        self._id_to_info: dict[str, MeshProfileInfo] = {}
        self._load_mesh_profiles()

    def _load_mesh_profiles(self) -> None:
        """Load mesh profiles from the Bluetooth SIG YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load mesh profile UUIDs
        mesh_profiles_yaml = base_path / "mesh_profiles.yaml"
        if mesh_profiles_yaml.exists():
            for item in load_yaml_uuids(mesh_profiles_yaml):
                try:
                    uuid = parse_bluetooth_uuid(item["uuid"])
                    name = item["name"]
                    mesh_profile_id = item["id"]

                    info = MeshProfileInfo(uuid=uuid, name=name, id=mesh_profile_id)

                    # Store by UUID string for fast lookup
                    self._mesh_profiles[uuid.short_form.upper()] = info
                    self._name_to_info[name.lower()] = info
                    self._id_to_info[mesh_profile_id] = info

                except (KeyError, ValueError):
                    # Skip malformed entries
                    continue

    def get_mesh_profile_info(self, uuid: str | int | BluetoothUUID) -> MeshProfileInfo | None:
        """Get mesh profile information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        try:
            bt_uuid = parse_bluetooth_uuid(uuid)
            return self._mesh_profiles.get(bt_uuid.short_form.upper())
        except ValueError:
            return None

    def get_mesh_profile_info_by_name(self, name: str) -> MeshProfileInfo | None:
        """Get mesh profile information by name (case insensitive).

        Args:
            name: The mesh profile name to look up

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        return self._name_to_info.get(name.lower())

    def get_mesh_profile_info_by_id(self, mesh_profile_id: str) -> MeshProfileInfo | None:
        """Get mesh profile information by mesh profile ID.

        Args:
            mesh_profile_id: The mesh profile ID to look up

        Returns:
            MeshProfileInfo if found, None otherwise
        """
        return self._id_to_info.get(mesh_profile_id)

    def is_mesh_profile_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known mesh profile.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known mesh profile, False otherwise
        """
        return self.get_mesh_profile_info(uuid) is not None

    def get_all_mesh_profiles(self) -> list[MeshProfileInfo]:
        """Get all mesh profiles in the registry.

        Returns:
            List of all MeshProfileInfo objects
        """
        return list(self._mesh_profiles.values())


# Global instance for convenience
mesh_profiles_registry = MeshProfilesRegistry.get_instance()
