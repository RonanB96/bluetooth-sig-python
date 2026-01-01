"""Members registry for Bluetooth SIG member UUIDs."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.types.registry.member_uuids import MemberInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class MembersRegistry(BaseUUIDRegistry[MemberInfo]):
    """Registry for Bluetooth SIG member company UUIDs."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/member_uuids.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> MemberInfo:
        """Create MemberInfo from YAML data."""
        return MemberInfo(
            uuid=uuid,
            name=uuid_data["name"],
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> MemberInfo:
        """Create runtime MemberInfo from entry."""
        return MemberInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
        )

    def get_member_name(self, uuid: str | BluetoothUUID) -> str | None:
        """Get member company name by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

        Returns:
            Member company name, or None if not found
        """
        info = self.get_info(uuid)
        return info.name if info else None

    def is_member_uuid(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID is a registered member company UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is a member UUID, False otherwise
        """
        return self.get_info(uuid) is not None

    def get_all_members(self) -> list[MemberInfo]:
        """Get all registered member companies.

        Returns:
            List of all MemberInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())

    def get_member_info_by_name(self, name: str) -> MemberInfo | None:
        """Get member information by company name.

        Args:
            name: Company name (case-insensitive)

        Returns:
            MemberInfo object, or None if not found
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.name.lower() == name.lower():
                return info
        return None


# Global instance
members_registry = MembersRegistry.get_instance()
