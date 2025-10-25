"""Member UUID registry for Bluetooth SIG member companies."""

from __future__ import annotations

import threading

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

from .utils import find_bluetooth_sig_path, load_yaml_uuids, normalize_uuid_string, parse_bluetooth_uuid


class MemberInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG member company."""

    uuid: BluetoothUUID
    name: str


class MembersRegistry:
    """Registry for Bluetooth SIG member company UUIDs."""

    def __init__(self) -> None:
        """Initialize the members registry."""
        self._lock = threading.RLock()
        self._members: dict[str, MemberInfo] = {}  # normalized_uuid -> MemberInfo
        self._members_by_name: dict[str, MemberInfo] = {}  # lower_name -> MemberInfo

        try:
            self._load_members()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _load_members(self) -> None:
        """Load member UUIDs from YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load member UUIDs
        member_yaml = base_path / "member_uuids.yaml"
        if member_yaml.exists():
            for uuid_info in load_yaml_uuids(member_yaml):
                uuid = normalize_uuid_string(uuid_info["uuid"])

                bt_uuid = BluetoothUUID(uuid)
                info = MemberInfo(uuid=bt_uuid, name=uuid_info["name"])
                # Store using short form as key for easy lookup
                self._members[bt_uuid.short_form.upper()] = info
                # Also store by name for reverse lookup
                self._members_by_name[uuid_info["name"].lower()] = info

    def get_member_name(self, uuid: str | int | BluetoothUUID) -> str | None:
        """Get member company name by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

        Returns:
            Member company name, or None if not found
        """
        with self._lock:
            try:
                bt_uuid = parse_bluetooth_uuid(uuid)

                # Get the short form (16-bit) for lookup
                short_key = bt_uuid.short_form.upper()
                if short_key in self._members:
                    return self._members[short_key].name

                return None
            except ValueError:
                return None

    def is_member_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID is a registered member company UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is a member UUID, False otherwise
        """
        return self.get_member_name(uuid) is not None

    def get_all_members(self) -> list[MemberInfo]:
        """Get all registered member companies.

        Returns:
            List of all MemberInfo objects
        """
        with self._lock:
            return list(self._members.values())

    def get_member_info_by_name(self, name: str) -> MemberInfo | None:
        """Get member information by company name.

        Args:
            name: Company name (case-insensitive)

        Returns:
            MemberInfo object, or None if not found
        """
        with self._lock:
            return self._members_by_name.get(name.lower())


# Global instance
members_registry = MembersRegistry()
