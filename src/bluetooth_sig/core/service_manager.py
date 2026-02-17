"""Discovered service lifecycle management.

Owns the only mutable state from the original translator: the _services dict.
Handles process_services, get_service_by_uuid, discovered_services, clear_services.
"""

from __future__ import annotations

from typing import Any

from ..gatt.services.base import BaseGattService
from ..gatt.services.registry import GattServiceRegistry
from ..types import CharacteristicInfo
from ..types.gatt_enums import ValueType
from ..types.uuid import BluetoothUUID

# Type alias for characteristic data in process_services
CharacteristicDataDict = dict[str, Any]


class ServiceManager:
    """Manages discovered GATT services.

    This is the **only** delegate that holds mutable state — the dict of
    discovered services keyed by normalised UUID strings.
    """

    def __init__(self) -> None:
        """Initialise with an empty services dict."""
        # Performance: Use str keys (normalised UUIDs) for fast dict lookups
        self._services: dict[str, BaseGattService] = {}

    def process_services(self, services: dict[str, dict[str, CharacteristicDataDict]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics

        """
        for uuid_str, service_data in services.items():
            uuid = BluetoothUUID(uuid_str)
            characteristics: dict[BluetoothUUID, CharacteristicInfo] = {}
            for char_uuid_str, char_data in service_data.get("characteristics", {}).items():
                char_uuid = BluetoothUUID(char_uuid_str)
                vtype_raw = char_data.get("value_type", "bytes")
                if isinstance(vtype_raw, str):
                    value_type = ValueType(vtype_raw)
                elif isinstance(vtype_raw, ValueType):
                    value_type = vtype_raw
                else:
                    value_type = ValueType.BYTES
                characteristics[char_uuid] = CharacteristicInfo(
                    uuid=char_uuid,
                    name=char_data.get("name", ""),
                    unit=char_data.get("unit", ""),
                    value_type=value_type,
                )
            service = GattServiceRegistry.create_service(uuid, characteristics)
            if service:
                self._services[str(uuid)] = service

    def get_service_by_uuid(self, uuid: str) -> BaseGattService | None:
        """Get a service instance by UUID.

        Args:
            uuid: The service UUID

        Returns:
            Service instance if found, None otherwise

        """
        return self._services.get(uuid)

    @property
    def discovered_services(self) -> list[BaseGattService]:
        """Get list of discovered service instances.

        Returns:
            List of discovered service instances

        """
        return list(self._services.values())

    def clear_services(self) -> None:
        """Clear all discovered services."""
        self._services.clear()
