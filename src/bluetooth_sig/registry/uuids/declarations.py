"""Declarations registry for Bluetooth SIG GATT attribute declarations."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.declarations import DeclarationInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class DeclarationsRegistry(BaseRegistry[DeclarationInfo]):
    """Registry for Bluetooth SIG GATT attribute declarations."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/declarations.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> DeclarationInfo:
        """Create DeclarationInfo from YAML data."""
        return DeclarationInfo(
            uuid=uuid,
            name=uuid_data["name"],
            id=uuid_data["id"],
            summary="",
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> DeclarationInfo:
        """Create runtime DeclarationInfo from entry."""
        return DeclarationInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
            id=getattr(entry, "id", ""),
            summary=getattr(entry, "summary", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of declarations data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_declaration_info(self, uuid: str | int | BluetoothUUID) -> DeclarationInfo | None:
        """Get declaration information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            DeclarationInfo if found, None otherwise
        """
        return self.get_info(uuid)

    def get_declaration_info_by_name(self, name: str) -> DeclarationInfo | None:
        """Get declaration information by name (case insensitive).

        Args:
            name: The declaration name to look up

        Returns:
            DeclarationInfo if found, None otherwise
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.name.lower() == name.lower():
                return info
        return None

    def get_declaration_info_by_id(self, declaration_id: str) -> DeclarationInfo | None:
        """Get declaration information by declaration ID.

        Args:
            declaration_id: The declaration ID to look up

        Returns:
            DeclarationInfo if found, None otherwise
        """
        self._ensure_loaded()
        for info in self._canonical_store.values():
            if info.id == declaration_id:
                return info
        return None

    def is_declaration_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known declaration.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known declaration, False otherwise
        """
        return self.get_info(uuid) is not None

    def get_all_declarations(self) -> list[DeclarationInfo]:
        """Get all declarations in the registry.

        Returns:
            List of all DeclarationInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance for convenience
declarations_registry = DeclarationsRegistry.get_instance()
