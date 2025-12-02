"""Object types registry for Bluetooth SIG object type definitions."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.object_types import ObjectTypeInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class ObjectTypesRegistry(BaseUUIDRegistry[ObjectTypeInfo]):
    """Registry for Bluetooth SIG Object Transfer Service (OTS) object types."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/object_types.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> ObjectTypeInfo:
        """Create ObjectTypeInfo from YAML data."""
        return ObjectTypeInfo(
            uuid=uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> ObjectTypeInfo:
        """Create runtime ObjectTypeInfo from entry."""
        return ObjectTypeInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of object types data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_object_type_info(self, uuid: str | BluetoothUUID) -> ObjectTypeInfo | None:
        """Get object type information by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x) or BluetoothUUID

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        return self.get_info(uuid)

    def get_object_type_info_by_name(self, name: str) -> ObjectTypeInfo | None:
        """Get object type information by name.

        Args:
            name: Object type name (case-insensitive)

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.name.lower() == name.lower():
                return info
        return None

    def get_object_type_info_by_id(self, object_type_id: str) -> ObjectTypeInfo | None:
        """Get object type information by ID.

        Args:
            object_type_id: Object type ID (e.g., "org.bluetooth.object.track")

        Returns:
            ObjectTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.id == object_type_id:
                return info
        return None

    def is_object_type_uuid(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID is a registered object type UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is an object type UUID, False otherwise
        """
        return self.get_info(uuid) is not None

    def get_all_object_types(self) -> list[ObjectTypeInfo]:
        """Get all registered object types.

        Returns:
            List of all ObjectTypeInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance
object_types_registry = ObjectTypesRegistry.get_instance()
