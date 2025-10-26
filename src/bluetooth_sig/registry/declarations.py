"""Declarations registry for Bluetooth SIG GATT attribute declarations."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class DeclarationInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth SIG GATT attribute declaration."""

    uuid: BluetoothUUID
    name: str
    id: str


class DeclarationsRegistry(BaseRegistry[DeclarationInfo]):
    """Registry for Bluetooth SIG GATT attribute declarations."""

    def __init__(self) -> None:
        """Initialize the declarations registry."""
        super().__init__()
        self._declarations: dict[str, DeclarationInfo] = {}
        self._name_to_info: dict[str, DeclarationInfo] = {}
        self._id_to_info: dict[str, DeclarationInfo] = {}
        self._load_declarations()

    def _load_declarations(self) -> None:
        """Load declarations from the Bluetooth SIG YAML file."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            return

        # Load declaration UUIDs
        declarations_yaml = base_path / "uuids" / "declarations.yaml"
        if declarations_yaml.exists():
            for item in load_yaml_uuids(declarations_yaml):
                try:
                    uuid = parse_bluetooth_uuid(item["uuid"])
                    name = item["name"]
                    declaration_id = item["id"]

                    info = DeclarationInfo(uuid=uuid, name=name, id=declaration_id)

                    # Store by UUID string for fast lookup
                    self._declarations[uuid.short_form.upper()] = info
                    self._name_to_info[name.lower()] = info
                    self._id_to_info[declaration_id] = info

                except (KeyError, ValueError):
                    # Skip malformed entries
                    continue

    def get_declaration_info(self, uuid: str | int | BluetoothUUID) -> DeclarationInfo | None:
        """Get declaration information by UUID.

        Args:
            uuid: The UUID to look up (string, int, or BluetoothUUID)

        Returns:
            DeclarationInfo if found, None otherwise
        """
        try:
            bt_uuid = parse_bluetooth_uuid(uuid)
            return self._declarations.get(bt_uuid.short_form.upper())
        except ValueError:
            return None

    def get_declaration_info_by_name(self, name: str) -> DeclarationInfo | None:
        """Get declaration information by name (case insensitive).

        Args:
            name: The declaration name to look up

        Returns:
            DeclarationInfo if found, None otherwise
        """
        return self._name_to_info.get(name.lower())

    def get_declaration_info_by_id(self, declaration_id: str) -> DeclarationInfo | None:
        """Get declaration information by declaration ID.

        Args:
            declaration_id: The declaration ID to look up

        Returns:
            DeclarationInfo if found, None otherwise
        """
        return self._id_to_info.get(declaration_id)

    def is_declaration_uuid(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known declaration.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known declaration, False otherwise
        """
        return self.get_declaration_info(uuid) is not None

    def get_all_declarations(self) -> list[DeclarationInfo]:
        """Get all declarations in the registry.

        Returns:
            List of all DeclarationInfo objects
        """
        return list(self._declarations.values())


# Global instance for convenience
declarations_registry = DeclarationsRegistry.get_instance()
