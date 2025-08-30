"""GATT hierarchy manager for device services."""

from __future__ import annotations

from typing import Dict, List, Optional

from .services import GattServiceRegistry
from .services.base import BaseGattService


class GattHierarchyManager:
    """Manager for GATT service hierarchy."""

    def __init__(self):
        """Initialize the GATT hierarchy manager."""
        self._services: Dict[str, BaseGattService] = {}

    def process_services(self, services: Dict[str, Dict[str, Dict]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics
        """
        for uuid, service_data in services.items():
            service = GattServiceRegistry.create_service(
                uuid, service_data.get("characteristics", {})
            )
            if service:
                self._services[uuid] = service

    def get_service(self, uuid: str) -> Optional[BaseGattService]:
        """Get a service by UUID."""
        return self._services.get(uuid)

    @property
    def supported_services(self) -> List[str]:
        """Get list of supported service UUIDs."""
        return GattServiceRegistry.supported_services()

    @property
    def discovered_services(self) -> List[BaseGattService]:
        """Get list of discovered services."""
        return list(self._services.values())


# Global instance for convenience
gatt_hierarchy = GattHierarchyManager()
