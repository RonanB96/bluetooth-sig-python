"""Protocol identifiers registry for Bluetooth SIG protocol definitions."""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.protocol_identifiers import ProtocolInfo
from bluetooth_sig.types.uuid import BluetoothUUID

__all__ = ["ProtocolIdentifiersRegistry", "ProtocolInfo", "protocol_identifiers_registry"]


class ProtocolIdentifiersRegistry(BaseUUIDRegistry[ProtocolInfo]):
    """Registry for Bluetooth protocol identifiers.

    Provides lookup of protocol information by UUID or name.
    Supports Classic Bluetooth protocols (L2CAP, RFCOMM, BNEP, AVDTP, etc.)
    and BLE protocols.
    """

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "assigned_numbers/uuids/protocol_identifiers.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> ProtocolInfo:
        """Create ProtocolInfo from YAML data."""
        return ProtocolInfo(
            uuid=uuid,
            name=uuid_data["name"],
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> ProtocolInfo:
        """Create runtime ProtocolInfo from entry."""
        return ProtocolInfo(
            uuid=uuid,
            name=getattr(entry, "name", ""),
        )

    def _load(self) -> None:
        """Perform the actual loading of protocol identifiers data."""
        base_path = find_bluetooth_sig_path()
        if base_path:
            yaml_path = base_path / self._load_yaml_path()
            if yaml_path.exists():
                self._load_from_yaml(yaml_path)
        self._loaded = True

    def get_protocol_info(self, uuid: str | BluetoothUUID) -> ProtocolInfo | None:
        """Get protocol information by UUID or name.

        Args:
            uuid: Protocol UUID (string, int, or BluetoothUUID) or protocol name

        Returns:
            ProtocolInfo if found, None otherwise

        Examples:
            >>> registry = ProtocolIdentifiersRegistry()
            >>> info = registry.get_protocol_info("0x0100")
            >>> if info:
            ...     print(info.name)  # "L2CAP"
            >>> info = registry.get_protocol_info("RFCOMM")
            >>> if info:
            ...     print(info.uuid.short_form)  # "0003"
        """
        return self.get_info(uuid)

    def get_protocol_info_by_name(self, name: str) -> ProtocolInfo | None:
        """Get protocol information by name (case insensitive).

        Args:
            name: The protocol name to look up (e.g., "L2CAP", "RFCOMM")

        Returns:
            ProtocolInfo if found, None otherwise
        """
        return self.get_info(name)

    def is_known_protocol(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID corresponds to a known protocol.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is a known protocol, False otherwise
        """
        self._ensure_loaded()
        return self.get_protocol_info(uuid) is not None

    def get_all_protocols(self) -> list[ProtocolInfo]:
        """Get all registered protocol identifiers.

        Returns:
            List of all ProtocolInfo objects
        """
        self._ensure_loaded()
        return list(self._canonical_store.values())


# Global instance for convenience
protocol_identifiers_registry = ProtocolIdentifiersRegistry.get_instance()
