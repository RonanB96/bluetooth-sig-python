"""SDO UUIDs registry for Bluetooth SIG Special Development Organization UUIDs."""

from __future__ import annotations

import re

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class SdoInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG SDO UUID."""

    uuid: BluetoothUUID
    name: str
    id: str


class SdoUuidsRegistry(BaseRegistry[SdoInfo]):
    """Registry for Bluetooth SIG Special Development Organization UUIDs."""

    def __init__(self) -> None:
        """Initialize the SDO UUIDs registry."""
        super().__init__()
        self._sdo_uuids: dict[str, SdoInfo] = {}
        self._name_to_info: dict[str, SdoInfo] = {}
        self._id_to_info: dict[str, SdoInfo] = {}
        self._load_sdo_uuids()

    def _normalize_name_for_id(self, name: str) -> str:
        """Normalize a name to create a valid ID string.

        Args:
            name: The name to normalize

        Returns:
            Normalized ID string
        """
        # Convert to lowercase, replace spaces and special chars with underscores
        normalized = re.sub(r"[^a-zA-Z0-9]", "_", name.lower())
        # Remove multiple consecutive underscores
        normalized = re.sub(r"_+", "_", normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip("_")
        return normalized

    def _load_sdo_uuids(self) -> None:
        """Load SDO UUIDs from the Bluetooth SIG YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load SDO UUIDs
        sdo_uuids_yaml = base_path / "uuids" / "sdo_uuids.yaml"
        if sdo_uuids_yaml.exists():
            for item in load_yaml_uuids(sdo_uuids_yaml):
                try:
                    uuid = parse_bluetooth_uuid(item["uuid"])
                    name = item["name"]

                    # Generate synthetic ID since SDO YAML doesn't have 'id' field
                    normalized_name = self._normalize_name_for_id(name)
                    sdo_id = f"org.bluetooth.sdo.{normalized_name}"

                    info = SdoInfo(uuid=uuid, name=name, id=sdo_id)

                    # Store by UUID string for fast lookup
                    self._sdo_uuids[uuid.short_form.upper()] = info
                    self._name_to_info[name.lower()] = info
                    self._id_to_info[sdo_id] = info

                except (KeyError, ValueError):
                    # Skip malformed entries
                    continue

    def get_sdo_info(self, uuid: str | int | BluetoothUUID) -> SdoInfo | None:
        """Get SDO information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            SdoInfo if found, None otherwise
        """
        try:
            bt_uuid = parse_bluetooth_uuid(uuid)
            return self._sdo_uuids.get(bt_uuid.short_form.upper())
        except ValueError:
            return None

    def get_sdo_info_by_name(self, name: str) -> SdoInfo | None:
        """Get SDO information by name (case insensitive).

        Args:
            name: The SDO name to look up

        Returns:
            SdoInfo if found, None otherwise
        """
        return self._name_to_info.get(name.lower())

    def get_sdo_info_by_id(self, sdo_id: str) -> SdoInfo | None:
        """Get SDO information by SDO ID.

        Args:
            sdo_id: The SDO ID to look up

        Returns:
            SdoInfo if found, None otherwise
        """
        return self._id_to_info.get(sdo_id)

    def is_sdo_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known SDO.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known SDO, False otherwise
        """
        return self.get_sdo_info(uuid) is not None

    def get_all_sdo_uuids(self) -> list[SdoInfo]:
        """Get all SDO UUIDs in the registry.

        Returns:
            List of all SdoInfo objects
        """
        return list(self._sdo_uuids.values())


# Global instance for convenience
sdo_uuids_registry = SdoUuidsRegistry.get_instance()
