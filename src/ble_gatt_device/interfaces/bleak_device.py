"""Bleak-based BLE device implementation for backend abstraction."""

import asyncio
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.client import BaseBleakClient

from ble_gatt_device.gatt.gatt_manager import gatt_hierarchy
from ble_gatt_device.interfaces.ble_device_interface import BLEDeviceInterface
from ble_gatt_device.utils import get_rssi_quality


class BleakBLEDevice(BLEDeviceInterface):
    """Bleak-based BLE device implementation."""

    def __init__(self, address: str):
        super().__init__(address)
        self._client: Optional[BaseBleakClient] = None
        # RSSI tracking attributes
        self._scan_rssi: Optional[int] = None
        self._scan_rssi_quality: Optional[str] = None
        self._connection_rssi: Optional[int] = None
        self._connection_rssi_quality: Optional[str] = None

    @property
    def _backend(self):
        """Get the Bleak backend safely."""
        if self._client and hasattr(self._client, "_backend"):
            return self._client._backend  # pylint: disable=protected-access
        return None

    async def _scan_for_device(self):
        """Scan for the target device and get RSSI information."""
        devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
        for address, (dev, adv_data) in devices.items():
            if address.lower() == self.address.lower():
                self._scan_rssi = adv_data.rssi
                self._scan_rssi_quality = get_rssi_quality(adv_data.rssi)
                return dev

        self._scan_rssi = None
        self._scan_rssi_quality = None
        return None

    async def _get_connection_rssi(self):
        """Get RSSI after connection is established."""
        self._connection_rssi = None
        self._connection_rssi_quality = None
        try:
            backend = self._backend
            if backend and hasattr(backend, "get_rssi"):
                connection_rssi = await backend.get_rssi()
                if connection_rssi is not None:
                    self._connection_rssi = connection_rssi
                    self._connection_rssi_quality = get_rssi_quality(connection_rssi)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    async def _discover_services_with_retry(self) -> bool:
        """Discover services with retry logic."""
        discovery_attempts = 0
        max_attempts = 3
        while discovery_attempts < max_attempts:
            try:
                services = self._client.services
                if services:
                    return True
                discovery_attempts += 1
                if discovery_attempts < max_attempts:
                    await asyncio.sleep(2)
            except Exception:  # pylint: disable=broad-exception-caught
                discovery_attempts += 1
                if discovery_attempts < max_attempts:
                    await asyncio.sleep(2)
        return False

    async def connect(self) -> bool:
        """Robust BLE connection with scan, RSSI, and service discovery diagnostics."""
        self._client = None

        try:
            # Scan for device
            device = await self._scan_for_device()
            if not device:
                return False

            # Connect to device
            self._client = BleakClient(device, timeout=20.0)
            await self._client.connect()

            # Get connection RSSI
            await self._get_connection_rssi()

            # Check connection status
            if not self._client.is_connected:
                await self._client.disconnect()
                self._client = None
                return False

            # Delay for service discovery reliability
            await asyncio.sleep(0.5)

            # Discover services with retry
            if not await self._discover_services_with_retry():
                await self._client.disconnect()
                self._client = None
                return False

            return True
        except Exception:  # pylint: disable=broad-exception-caught
            self._client = None
            return False

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def get_rssi(self) -> Optional[int]:
        if not self._client or not self._client.is_connected:
            return None
        try:
            if hasattr(self._client, "get_rssi"):
                return await self._client.get_rssi()
            backend = self._backend
            if backend and hasattr(backend, "get_rssi"):
                return await backend.get_rssi()
            return None
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def _normalize_service_uuid(self, service_uuid: str) -> str:
        """Normalize service UUID format."""
        service_uuid = service_uuid.upper()
        if len(service_uuid) == 36:
            standard_suffix = "-0000-1000-8000-00805F9B34FB"
            if service_uuid.endswith(standard_suffix):
                service_uuid = service_uuid[4:8]
        return service_uuid

    def _build_services_dict(self, bleak_services):
        """Build services dictionary for gatt hierarchy processing."""
        services_dict = {}
        for service in bleak_services:
            service_uuid = self._normalize_service_uuid(str(service.uuid))
            characteristics = {}
            for char in service.characteristics:
                char_uuid = str(char.uuid)
                characteristics[char_uuid] = {"properties": char.properties}
            services_dict[service_uuid] = {"characteristics": characteristics}
        return services_dict

    def _build_uuid_mapping(self, bleak_services):
        """Build mapping between transformed and original UUIDs."""
        uuid_mapping = {}
        for service in bleak_services:
            for char in service.characteristics:
                original_uuid = str(char.uuid)
                transformed_uuid = original_uuid.replace("-", "").upper()
                uuid_mapping[transformed_uuid] = original_uuid
        return uuid_mapping

    async def _read_characteristic_values(self, uuid_mapping):
        """Read values from all readable characteristics."""
        values = {}
        for service in gatt_hierarchy.discovered_services:
            for transformed_uuid, char in service.characteristics.items():
                if "read" in char.properties:
                    original_uuid = uuid_mapping.get(transformed_uuid)
                    if original_uuid:
                        try:
                            value = await self._client.read_gatt_char(original_uuid)
                            values[transformed_uuid] = value
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass
        return values

    async def read_characteristics(self) -> dict:
        if not self._client:
            return {}
        try:
            bleak_services = self._client.services

            # Build services dictionary and process with gatt hierarchy
            services_dict = self._build_services_dict(bleak_services)
            gatt_hierarchy.process_services(services_dict)

            # Build UUID mapping and read characteristic values
            uuid_mapping = self._build_uuid_mapping(bleak_services)
            values = await self._read_characteristic_values(uuid_mapping)

            return values
        except Exception:  # pylint: disable=broad-exception-caught
            return {}

    async def read_parsed_characteristics(self) -> dict:
        raw_values = await self.read_characteristics()
        parsed_values = {
            "device_info": {
                "address": self.address,
                "rssi": await self.get_rssi(),
                "connected": self._client.is_connected if self._client else False,
            },
            "characteristics": {},
        }
        if not raw_values:
            return parsed_values
        for service in gatt_hierarchy.discovered_services:
            for uuid, char in service.characteristics.items():
                if uuid in raw_values:
                    try:
                        raw_data = raw_values[uuid]
                        parsed_value = char.parse_value(raw_data)
                        parsed_values["characteristics"][uuid] = {
                            "characteristic": char.__class__.__name__,
                            "value": parsed_value,
                            "unit": getattr(char, "unit", ""),
                            "raw": raw_data,
                        }
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
        return parsed_values

    async def get_device_info(self) -> dict:
        if not self._client:
            return {"connected": False}
        try:
            bleak_services = self._client.services
            device_info = {
                "connected": True,
                "address": self.address,
                "rssi": await self.get_rssi(),
                "services": {},
            }
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
