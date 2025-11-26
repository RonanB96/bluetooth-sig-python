"""Units registry for Bluetooth SIG unit definitions."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.common import BaseUuidInfo
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.uuid import BluetoothUUID


class UnitInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG unit."""

    id: str


class UnitsRegistry(BaseRegistry[UnitInfo]):
    """Registry for Bluetooth SIG unit UUIDs."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "units.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], bt_uuid: BluetoothUUID) -> UnitInfo:
        """Create UnitInfo from YAML data."""
        return UnitInfo(
            uuid=bt_uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
        )

    def _create_runtime_info(self, entry: object, bt_uuid: BluetoothUUID) -> UnitInfo:
        """Create runtime UnitInfo from entry."""
        return UnitInfo(
            uuid=bt_uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of units data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_unit_info(self, uuid: str | int | BluetoothUUID) -> UnitInfo | None:
        """Get unit information by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(uuid)

    def get_unit_info_by_name(self, name: str) -> UnitInfo | None:
        """Get unit information by name.

        Args:
            name: Unit name (case-insensitive)

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(name)

    def get_unit_info_by_id(self, unit_id: str) -> UnitInfo | None:
        """Get unit information by ID.

        Args:
            unit_id: Unit ID (e.g., "org.bluetooth.unit.celsius")

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(unit_id)

    def is_unit_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID is a registered unit UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is a unit UUID, False otherwise
        """
        return self.get_unit_info(uuid) is not None

    def get_all_units(self) -> list[UnitInfo]:
        """Get all registered units.

        Returns:
            List of all UnitInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._canonical_store.values())


# Global instance
units_registry = UnitsRegistry()
