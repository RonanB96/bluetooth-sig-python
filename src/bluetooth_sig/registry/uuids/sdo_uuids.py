"""SDO UUIDs registry for Bluetooth SIG Special Development Organization UUIDs."""

from __future__ import annotations

import re

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.types.registry.sdo_uuids import SdoUuidInfo as SdoInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class SdoUuidsRegistry(BaseUUIDRegistry[SdoInfo]):
    """Registry for Bluetooth SIG Special Development Organization UUIDs."""

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

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/sdo_uuids.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> SdoInfo:
        """Create SdoInfo from YAML data."""
        name = uuid_data["name"]
        return SdoInfo(
            uuid=uuid,
            name=name,
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> SdoInfo:
        """Create runtime SdoInfo from entry."""
        return SdoInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
        )

    def get_sdo_info(self, uuid: str | BluetoothUUID) -> SdoInfo | None:
        """Get SDO information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            SdoInfo if found, None otherwise
        """
        return self.get_info(uuid)

    def get_sdo_info_by_name(self, name: str) -> SdoInfo | None:
        """Get SDO information by name (case insensitive).

        Args:
            name: The SDO name to look up

        Returns:
            SdoInfo if found, None otherwise
        """
        return self.get_info(name)

    def get_sdo_info_by_id(self, sdo_id: str) -> SdoInfo | None:
        """Get SDO information by SDO ID.

        Args:
            sdo_id: The SDO ID to look up

        Returns:
            SdoInfo if found, None otherwise
        """
        return self.get_info(sdo_id)

    def is_sdo_uuid(self, uuid: str | BluetoothUUID) -> bool:
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
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance for convenience
sdo_uuids_registry = SdoUuidsRegistry.get_instance()
