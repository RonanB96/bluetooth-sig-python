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

    def __str__(self) -> str:
        """Return string representation of the device.

        Returns:
            str: String representation including device address
        """
        return f"BLEGATTDevice(address={self.address})"

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
            # Get services from device (automatically discovered on connect)
            bleak_services = self._client.services

            # Convert Bleak services to our expected format
            services_dict = {}
            for service in bleak_services:
                service_uuid = str(service.uuid).upper()
                # Convert full UUID to short form if it's a standard Bluetooth UUID
                if len(service_uuid) == 36:
                    standard_suffix = "-0000-1000-8000-00805F9B34FB"
                    if service_uuid.endswith(standard_suffix):
                        service_uuid = service_uuid[4:8]

                characteristics = {}
                for char in service.characteristics:
                    char_uuid = str(char.uuid)
                    characteristics[char_uuid] = {"properties": char.properties}

                services_dict[service_uuid] = {"characteristics": characteristics}

            # Process services through our hierarchy
            gatt_hierarchy.process_services(services_dict)
            values = {}

            # Create mapping from transformed UUID back to original UUID
            uuid_mapping = {}
            for service in bleak_services:
                for char in service.characteristics:
                    original_uuid = str(char.uuid)
                    transformed_uuid = original_uuid.replace("-", "").upper()
                    uuid_mapping[transformed_uuid] = original_uuid

            # Read all readable characteristics using original UUIDs
            for service in gatt_hierarchy.discovered_services:
                for transformed_uuid, char in service.characteristics.items():
                    if "read" in char.properties:
                        original_uuid = uuid_mapping.get(transformed_uuid)
                        if original_uuid:
                            try:
                                value = await self._client.read_gatt_char(original_uuid)
                                # Store with transformed UUID for consistency
                                values[transformed_uuid] = value
                            except Exception:  # pylint: disable=broad-exception-caught
                                pass  # Skip failed reads

            return values

        except Exception:  # pylint: disable=broad-exception-caught
            return {}

    async def read_parsed_characteristics(self) -> Dict:
        """Read and parse all supported characteristics.

        Returns:
            Dict: UUID to parsed value mapping for all readable characteristics
        """
        raw_values = await self.read_characteristics()
        parsed_values = {}

        if not raw_values:
            return parsed_values

        # Parse using our GATT framework
        for service in gatt_hierarchy.discovered_services:
            for uuid, char in service.characteristics.items():
                if uuid in raw_values:
                    try:
                        raw_data = raw_values[uuid]
                        parsed_value = char.parse_value(raw_data)
                        parsed_values[uuid] = {
                            "characteristic": char.__class__.__name__,
                            "value": parsed_value,
                            "unit": getattr(char, "unit", ""),
                            "raw": raw_data,
                        }
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass  # Skip failed parsing

        return parsed_values

    async def get_device_info(self) -> Dict:
        """Get device information and discovered services.

        Returns:
            Dict: Device information including services and characteristics
        """
        if not self._client:
            return {"connected": False}

        try:
            # Get services from device (automatically discovered on connect)
            bleak_services = self._client.services

            device_info = {"connected": True, "address": self.address, "services": {}}

            for service in bleak_services:
                service_uuid = str(service.uuid).upper()
                service_info = {"uuid": service_uuid, "characteristics": {}}

                for char in service.characteristics:
                    char_info = {
                        "uuid": str(char.uuid),
                        "properties": char.properties,
                        "descriptors": [str(desc.uuid) for desc in char.descriptors],
                    }
                    service_info["characteristics"][str(char.uuid)] = char_info

                device_info["services"][service_uuid] = service_info

            return device_info

        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"connected": False, "error": str(e)}
