"""Service classes registry for Bluetooth SIG service class UUIDs."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.service_class import ServiceClassInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class ServiceClassesRegistry(BaseUUIDRegistry[ServiceClassInfo]):
    """Registry for Bluetooth SIG service class definitions."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/service_classes.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> ServiceClassInfo:
        """Create ServiceClassInfo from YAML data."""
        return ServiceClassInfo(
            uuid=uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> ServiceClassInfo:
        """Create runtime ServiceClassInfo from entry."""
        return ServiceClassInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of service classes data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_service_class_info(self, uuid: str | BluetoothUUID) -> ServiceClassInfo | None:
        """Get service class information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        return self.get_info(uuid)

    def get_service_class_info_by_name(self, name: str) -> ServiceClassInfo | None:
        """Get service class information by name (case insensitive).

        Args:
            name: The service class name to look up

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        return self.get_info(name)

    def get_service_class_info_by_id(self, service_class_id: str) -> ServiceClassInfo | None:
        """Get service class information by service class ID.

        Args:
            service_class_id: The service class ID to look up

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        return self.get_info(service_class_id)

    def is_service_class_uuid(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known service class.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known service class, False otherwise
        """
        return self.get_service_class_info(uuid) is not None

    def get_all_service_classes(self) -> list[ServiceClassInfo]:
        """Get all service classes in the registry.

        Returns:
            List of all ServiceClassInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._canonical_store.values())


# Global instance for convenience
service_classes_registry = ServiceClassesRegistry.get_instance()
