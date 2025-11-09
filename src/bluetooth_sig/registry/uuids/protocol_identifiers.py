"""Protocol identifiers registry for Bluetooth SIG protocol definitions."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path, load_yaml_uuids, parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID

__all__ = ["ProtocolIdentifiersRegistry", "ProtocolInfo", "protocol_identifiers_registry"]


class ProtocolInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Information about a Bluetooth protocol identifier.

    Attributes:
        uuid: The protocol's Bluetooth UUID
        name: Human-readable protocol name (e.g., "L2CAP", "RFCOMM")
    """

    uuid: BluetoothUUID
    name: str


class ProtocolIdentifiersRegistry(BaseRegistry[ProtocolInfo]):
    """Registry for Bluetooth protocol identifiers.

    Provides lookup of protocol information by UUID or name.
    Supports Classic Bluetooth protocols (L2CAP, RFCOMM, BNEP, AVDTP, etc.)
    and BLE protocols.
    """

    def __init__(self) -> None:
        """Initialize the protocol identifiers registry."""
        super().__init__()
        self._protocols: dict[str, ProtocolInfo] = {}
        self._name_to_info: dict[str, ProtocolInfo] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Ensure the registry is loaded (thread-safe lazy loading)."""
        if self._loaded:
            return
        
        with self._lock:
            if self._loaded:
                return
            
            base_path = find_bluetooth_sig_path()
            if not base_path:
                self._loaded = True
                return

            # Load protocol identifier UUIDs
            protocol_identifiers_yaml = base_path / "protocol_identifiers.yaml"
            if protocol_identifiers_yaml.exists():
                for item in load_yaml_uuids(protocol_identifiers_yaml):
                    try:
                        uuid = parse_bluetooth_uuid(item["uuid"])
                        name = item["name"]

                        info = ProtocolInfo(uuid=uuid, name=name)

                        # Store by UUID short form for fast lookup
                        self._protocols[uuid.short_form.upper()] = info
                        self._name_to_info[name.lower()] = info

                    except (KeyError, ValueError):
                        # Skip malformed entries
                        continue
            self._loaded = True

    def get_protocol_info(self, identifier: str | int | BluetoothUUID) -> ProtocolInfo | None:
        """Get protocol information by UUID or name.

        Args:
            identifier: Protocol UUID (string, int, or BluetoothUUID) or protocol name

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
        self._ensure_loaded()
        # Try as UUID first
        try:
            bt_uuid = parse_bluetooth_uuid(identifier)
            return self._protocols.get(bt_uuid.short_form.upper())
        except (ValueError, TypeError):
            pass

        # Try as name (case-insensitive)
        if isinstance(identifier, str):
            return self._name_to_info.get(identifier.lower())

        return None

    def get_protocol_info_by_name(self, name: str) -> ProtocolInfo | None:
        """Get protocol information by name (case insensitive).

        Args:
            name: The protocol name to look up (e.g., "L2CAP", "RFCOMM")

        Returns:
            ProtocolInfo if found, None otherwise
        """
        self._ensure_loaded()
        return self._name_to_info.get(name.lower())

    def is_known_protocol(self, uuid: str | int | BluetoothUUID) -> bool:
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
        return list(self._protocols.values())

    def is_l2cap(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if UUID is L2CAP protocol.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is L2CAP (0x0100), False otherwise
        """
        self._ensure_loaded()
        info = self.get_protocol_info(uuid)
        return info is not None and info.name.upper() == "L2CAP"

    def is_rfcomm(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if UUID is RFCOMM protocol.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is RFCOMM (0x0003), False otherwise
        """
        self._ensure_loaded()
        info = self.get_protocol_info(uuid)
        return info is not None and info.name.upper() == "RFCOMM"

    def is_avdtp(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if UUID is AVDTP protocol.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is AVDTP (0x0019), False otherwise
        """
        self._ensure_loaded()
        info = self.get_protocol_info(uuid)
        return info is not None and info.name.upper() == "AVDTP"

    def is_bnep(self, uuid: str | int | BluetoothUUID) -> bool:
        """Check if UUID is BNEP protocol.

        Args:
            uuid: The UUID to check

        Returns:
            True if the UUID is BNEP (0x000F), False otherwise
        """
        self._ensure_loaded()
        info = self.get_protocol_info(uuid)
        return info is not None and info.name.upper() == "BNEP"


# Global instance for convenience
protocol_identifiers_registry = ProtocolIdentifiersRegistry.get_instance()
