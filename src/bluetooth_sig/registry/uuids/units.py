"""Units registry for Bluetooth SIG unit definitions."""

from __future__ import annotations

import threading

import msgspec

from bluetooth_sig.registry.utils import (
    find_bluetooth_sig_path,
    load_yaml_uuids,
    normalize_uuid_string,
    parse_bluetooth_uuid,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class UnitInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG unit."""

    uuid: BluetoothUUID
    name: str
    id: str


class UnitsRegistry:
    """Registry for Bluetooth SIG unit UUIDs."""

    def __init__(self) -> None:
        """Initialize the units registry."""
        self._lock = threading.RLock()
        self._units: dict[str, UnitInfo] = {}  # normalized_uuid -> UnitInfo
        self._units_by_name: dict[str, UnitInfo] = {}  # lower_name -> UnitInfo
        self._units_by_id: dict[str, UnitInfo] = {}  # id -> UnitInfo

        try:
            self._load_units()
        except (FileNotFoundError, Exception):  # pylint: disable=broad-exception-caught
            # If YAML loading fails, continue with empty registry
            pass

    def _load_units(self) -> None:
        """Load unit UUIDs from YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load unit UUIDs
        units_yaml = base_path / "units.yaml"
        if units_yaml.exists():
            for unit_info in load_yaml_uuids(units_yaml):
                uuid = normalize_uuid_string(unit_info["uuid"])

                bt_uuid = BluetoothUUID(uuid)
                info = UnitInfo(uuid=bt_uuid, name=unit_info["name"], id=unit_info["id"])
                # Store using short form as key for easy lookup
                self._units[bt_uuid.short_form.upper()] = info
                # Also store by name and id for reverse lookup
                self._units_by_name[unit_info["name"].lower()] = info
                self._units_by_id[unit_info["id"]] = info

    def get_unit_info(self, uuid: str | int | BluetoothUUID) -> UnitInfo | None:
        """Get unit information by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

        Returns:
            UnitInfo object, or None if not found
        """
        with self._lock:
            try:
                bt_uuid = parse_bluetooth_uuid(uuid)

                # Get the short form (16-bit) for lookup
                short_key = bt_uuid.short_form.upper()
                return self._units.get(short_key)
            except ValueError:
                return None

    def get_unit_info_by_name(self, name: str) -> UnitInfo | None:
        """Get unit information by name.

        Args:
            name: Unit name (case-insensitive)

        Returns:
            UnitInfo object, or None if not found
        """
        with self._lock:
            return self._units_by_name.get(name.lower())

    def get_unit_info_by_id(self, unit_id: str) -> UnitInfo | None:
        """Get unit information by ID.

        Args:
            unit_id: Unit ID (e.g., "org.bluetooth.unit.celsius")

        Returns:
            UnitInfo object, or None if not found
        """
        with self._lock:
            return self._units_by_id.get(unit_id)

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
        with self._lock:
            return list(self._units.values())


# Global instance
units_registry = UnitsRegistry()
