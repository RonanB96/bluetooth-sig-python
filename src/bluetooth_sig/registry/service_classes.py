"""Service classes registry for Bluetooth SIG service class definitions."""

from __future__ import annotations

import threading
from dataclasses import dataclass

from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


@dataclass(frozen=True)
class ServiceClassInfo:
    """Information about a Bluetooth SIG service class."""

    uuid: BluetoothUUID
    name: str
    id: str


class ServiceClassesRegistry:
    """Registry for Bluetooth SIG service class definitions."""

    _instance: ServiceClassesRegistry | None = None
    _lock = threading.RLock()

    def __init__(self) -> None:
        """Initialize the service classes registry."""
        self._service_classes: dict[str, ServiceClassInfo] = {}
        self._name_to_info: dict[str, ServiceClassInfo] = {}
        self._id_to_info: dict[str, ServiceClassInfo] = {}
        self._load_service_classes()

    def _load_service_classes(self) -> None:
        """Load service classes from the Bluetooth SIG YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load service class UUIDs
        service_classes_yaml = base_path / "service_classes.yaml"
        if service_classes_yaml.exists():
            for item in load_yaml_uuids(service_classes_yaml):
                try:
                    uuid = parse_bluetooth_uuid(item["uuid"])
                    name = item["name"]
                    service_class_id = item["id"]

                    info = ServiceClassInfo(
                        uuid=uuid,
                        name=name,
                        id=service_class_id
                    )

                    # Store by UUID string for fast lookup
                    self._service_classes[uuid.short_form.upper()] = info
                    self._name_to_info[name.lower()] = info
                    self._id_to_info[service_class_id] = info

                except (KeyError, ValueError):
                    # Skip malformed entries
                    continue

    @classmethod
    def get_instance(cls) -> ServiceClassesRegistry:
        """Get the singleton instance of the service classes registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_service_class_info(self, uuid: str | int | BluetoothUUID) -> ServiceClassInfo | None:
        """Get service class information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        try:
            bt_uuid = parse_bluetooth_uuid(uuid)
            return self._service_classes.get(bt_uuid.short_form.upper())
        except ValueError:
            return None

    def get_service_class_info_by_name(self, name: str) -> ServiceClassInfo | None:
        """Get service class information by name (case insensitive).

        Args:
            name: The service class name to look up

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        return self._name_to_info.get(name.lower())

    def get_service_class_info_by_id(self, service_class_id: str) -> ServiceClassInfo | None:
        """Get service class information by service class ID.

        Args:
            service_class_id: The service class ID to look up

        Returns:
            ServiceClassInfo if found, None otherwise
        """
        return self._id_to_info.get(service_class_id)

    def is_service_class_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
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
        return list(self._service_classes.values())


# Global instance for convenience
service_classes_registry = ServiceClassesRegistry.get_instance()
