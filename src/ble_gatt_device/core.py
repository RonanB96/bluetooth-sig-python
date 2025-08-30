"""Core BLE GATT device functionality."""

from __future__ import annotations

from typing import Dict, Optional

from bleak import BleakClient
from bleak.backends.client import BaseBleakClient

from .gatt.gatt_manager import gatt_hierarchy


class BLEGATTDevice:
    """BLE GATT device wrapper."""

    def __init__(self, address: str):
        """Initialize the BLE GATT device.

        Args:
            address: The BLE device address
        """
        self.address = address
        self._client: Optional[BaseBleakClient] = None

    async def connect(self) -> bool:
        """Connect to the BLE device.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._client = BleakClient(self.address)
            await self._client.connect()
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            self._client = None
            return False

    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def read_characteristics(self) -> Dict:
        """Read all supported characteristics.

        Returns:
            Dict: UUID to value mapping for all readable characteristics
        """
        if not self._client:
            return {}

        try:
            services = await self._client.get_services()  # pylint: disable=no-member
            gatt_hierarchy.process_services(services)
            values = {}

            for service in gatt_hierarchy.discovered_services:
                for uuid, char in service.characteristics.items():
                    if "read" in char.properties:
                        try:
                            value = await self._client.read_gatt_char(uuid)
                            values[uuid] = value
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass  # Skip failed reads

            return values

        except Exception:  # pylint: disable=broad-exception-caught
            return {}
