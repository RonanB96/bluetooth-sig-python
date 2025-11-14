"""Object types registry for Bluetooth SIG OTS object type definitions."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class ObjectTypeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG object type."""

    uuid: BluetoothUUID
    name: str
    id: str


class ObjectTypesRegistry(BaseRegistry[ObjectTypeInfo]):
    """Registry for Bluetooth SIG Object Transfer Service (OTS) object types."""

    def __init__(self) -> None:
        """Initialize the object types registry."""
        super().__init__()
        self._object_types: dict[str, ObjectTypeInfo] = {}  # normalized_uuid -> ObjectTypeInfo
        self._object_types_by_name: dict[str, ObjectTypeInfo] = {}  # lower_name -> ObjectTypeInfo
        self._object_types_by_id: dict[str, ObjectTypeInfo] = {}  # id -> ObjectTypeInfo

        try:  # pylint: disable=duplicate-code  # Standard exception handling pattern for registry YAML loading
            self._load_object_types()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _load_object_types(self) -> None:
        """Load object type UUIDs from YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            self._loaded = True
            return

        # Load object type UUIDs
        object_types_yaml = base_path / "object_types.yaml"
        if object_types_yaml.exists():
            for object_type_info in load_yaml_uuids(object_types_yaml):
                try:
                    uuid = object_type_info["uuid"]

                    bt_uuid = BluetoothUUID(uuid)
                    info = ObjectTypeInfo(uuid=bt_uuid, name=object_type_info["name"], id=object_type_info["id"])
                    # Store using short form as key for easy lookup
                    self._object_types[bt_uuid.short_form.upper()] = info
                    # Also store by name and id for reverse lookup
                    self._object_types_by_name[object_type_info["name"].lower()] = info
                    self._object_types_by_id[object_type_info["id"]] = info
                except (KeyError, ValueError):
                    # Skip malformed entries
                    continue
        self._loaded = True

    def get_object_type_info(self, uuid: str | int | BluetoothUUID) -> ObjectTypeInfo | None:
        """Get object type information by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            try:
                bt_uuid = parse_bluetooth_uuid(uuid)

                # Get the short form (16-bit) for lookup
                short_key = bt_uuid.short_form.upper()
                return self._object_types.get(short_key)
            except ValueError:
                return None

    def get_object_type_info_by_name(self, name: str) -> ObjectTypeInfo | None:
        """Get object type information by name.

        Args:
            name: Object type name (case-insensitive)

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._object_types_by_name.get(name.lower())

    def get_object_type_info_by_id(self, object_type_id: str) -> ObjectTypeInfo | None:
        """Get object type information by ID.

        Args:
            object_type_id: Object type ID (e.g., "org.bluetooth.object.track")

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._object_types_by_id.get(object_type_id)

    def is_object_type_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID is a registered object type UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is an object type UUID, False otherwise
        """
        self._ensure_loaded()
        return self.get_object_type_info(uuid) is not None

    def get_all_object_types(self) -> list[ObjectTypeInfo]:
        """Get all registered object types.

        Returns:
            List of all ObjectTypeInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._object_types.values())


# Global instance
object_types_registry = ObjectTypesRegistry()
