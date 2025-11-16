"""Bleak-based connection manager moved to examples connection_managers.

This module imports Bleak at module import time so that attempting to
import it when Bleak is not available will fail fast (tests rely on
that behaviour).
"""

from __future__ import annotations

import asyncio
from typing import Callable
from venv import logger

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types.advertising import (
    AdvertisingData,
    AdvertisingDataStructures,
    CoreAdvertisingData,
    DeviceProperties,
)
from bluetooth_sig.types.data_types import CharacteristicInfo
from bluetooth_sig.types.device_types import DeviceService, ScannedDevice
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID


class BleakRetryConnectionManager(ConnectionManagerProtocol):
    """Connection manager using Bleak with retry support for robust connections."""

    supports_scanning = True  # Bleak supports scanning

    def __init__(
        self,
        address: str,
        timeout: float = 30.0,
        max_attempts: int = 3,
        disconnected_callback: Callable[[BleakClient], None] | None = None,
    ) -> None:
        """Initialize the connection manager with Bleak-compatible callback.

        Args:
            address: Bluetooth device address
            timeout: Connection timeout in seconds
            max_attempts: Maximum number of connection retry attempts
            disconnected_callback: Optional callback when device disconnects.
                                  Bleak-style: receives BleakClient as argument.

        """
        super().__init__(address)
        self.timeout = timeout
        self.max_attempts = max_attempts
        self._bleak_callback = disconnected_callback
        self._cached_services: list[DeviceService] | None = None
        self.client = self._create_client()

    def _create_client(self) -> BleakClient:
        """Create a BleakClient with current settings.

        Returns:
            Configured BleakClient instance

        """
        # Use the Bleak-style callback directly
        return BleakClient(self.address, timeout=self.timeout, disconnected_callback=self._bleak_callback)

    async def connect(self) -> None:
        """Connect to the device with retry logic."""
        last_exception = None
        for attempt in range(self.max_attempts):
            try:
                await self.client.connect()
                self._cached_services = None  # Clear cache on new connection
                return
            except (OSError, TimeoutError) as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
                else:
                    raise last_exception from None

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        self._cached_services = None  # Clear cache on disconnect
        await self.client.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.client.is_connected

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read a GATT characteristic."""
        raw_data = await self.client.read_gatt_char(str(char_uuid))
        return bytes(raw_data)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        """Write to a GATT characteristic.

        Args:
            char_uuid: UUID of the characteristic to write to
            data: Data to write
            response: If True, use write-with-response; if False, use write-without-response

        """
        await self.client.write_gatt_char(str(char_uuid), data, response=response)

    async def get_services(self) -> list[DeviceService]:
        """Get services from the BleakClient, converted to DeviceService objects.

        Services are cached after first retrieval. Bleak's client.services property
        is already cached by Bleak itself after initial discovery during connection.

        Returns:
            List of DeviceService instances with populated characteristics

        """
        # Return cached services if available
        if self._cached_services is not None:
            return self._cached_services

        device_services: list[DeviceService] = []

        # Bleak's client.services is already cached after initial discovery
        for bleak_service in self.client.services:
            # Convert Bleak service UUID to BluetoothUUID
            service_uuid = BluetoothUUID(bleak_service.uuid)

            # Try to get the service class from registry
            service_class = GattServiceRegistry.get_service_class(service_uuid)

            if service_class:
                # Create service instance
                service_instance = service_class()

                # Populate characteristics with actual class instances
                characteristics: dict[str, BaseCharacteristic] = {}
                for char in bleak_service.characteristics:
                    char_uuid = BluetoothUUID(char.uuid)

                    # Convert Bleak properties to GattProperty enum
                    properties: list[GattProperty] = []
                    for prop in char.properties:
                        try:
                            properties.append(GattProperty(prop))
                        except ValueError:
                            logger.warning(f"Unknown GattProperty from Bleak: {prop}")

                    # Try to get the characteristic class from registry
                    char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(char_uuid)

                    if char_class:
                        # Create characteristic instance with runtime properties from device
                        char_instance = char_class(properties=properties)
                        characteristics[str(char_uuid)] = char_instance
                    else:
                        # Fallback: Create UnknownCharacteristic for unrecognized UUIDs
                        char_info = CharacteristicInfo(
                            uuid=char_uuid,
                            name=char.description or f"Unknown Characteristic ({char_uuid.short_form}...)",
                            description=char.description or "",
                        )
                        char_instance = UnknownCharacteristic(info=char_info, properties=properties)
                        characteristics[str(char_uuid)] = char_instance

                # Type ignore needed due to dict invariance with union types
                device_services.append(DeviceService(service=service_instance, characteristics=characteristics))  # type: ignore[arg-type]

        # Cache the result
        self._cached_services = device_services
        return device_services

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications."""

        def adapted_callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
            callback(characteristic.uuid, bytes(data))

        await self.client.start_notify(str(char_uuid), adapted_callback)

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications."""
        await self.client.stop_notify(str(char_uuid))

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        """Read a GATT descriptor.

        Args:
            desc_uuid: UUID of the descriptor to read

        Returns:
            Raw descriptor data as bytes

        Raises:
            ValueError: If descriptor with the given UUID is not found

        """
        # Find the descriptor by UUID
        descriptor = None
        for service in self.client.services:
            for char in service.characteristics:
                for desc in char.descriptors:
                    if desc.uuid.lower() == str(desc_uuid).lower():
                        descriptor = desc
                        break
                if descriptor:
                    break
            if descriptor:
                break

        if not descriptor:
            raise ValueError(f"Descriptor with UUID {desc_uuid} not found")

        raw_data = await self.client.read_gatt_descriptor(descriptor.handle)
        return bytes(raw_data)

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        """Write to a GATT descriptor.

        Args:
            desc_uuid: UUID of the descriptor to write to
            data: Data to write

        Raises:
            ValueError: If descriptor with the given UUID is not found

        """
        # Find the descriptor by UUID
        descriptor = None
        for service in self.client.services:
            for char in service.characteristics:
                for desc in char.descriptors:
                    if desc.uuid.lower() == str(desc_uuid).lower():
                        descriptor = desc
                        break
                if descriptor:
                    break
            if descriptor:
                break

        if not descriptor:
            raise ValueError(f"Descriptor with UUID {desc_uuid} not found")

        await self.client.write_gatt_descriptor(descriptor.handle, data)

    async def pair(self) -> None:
        """Pair with the device.

        Raises an exception if pairing fails.

        """
        await self.client.pair()

    async def unpair(self) -> None:
        """Unpair from the device.

        Raises an exception if unpairing fails.

        """
        await self.client.unpair()

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Returns:
            RSSI value in dBm (typically negative, e.g., -50)

        Raises:
            NotImplementedError: If the backend doesn't support RSSI reading

        """
        # Bleak doesn't have a standard cross-platform RSSI method
        # This would need to be implemented per-backend
        raise NotImplementedError("RSSI reading not yet supported in Bleak connection manager")

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be called when the device disconnects.

        Args:
            callback: Function to call when device disconnects.

        Raises:
            NotImplementedError: Bleak requires disconnected_callback in __init__.
                                Use the disconnected_callback parameter when creating
                                the BleakRetryConnectionManager instead.

        """
        raise NotImplementedError(
            "Bleak requires disconnected_callback to be set during initialization. "
            "Pass it to the BleakRetryConnectionManager constructor instead."
        )

    @classmethod
    async def scan(cls, timeout: float = 5.0) -> list[ScannedDevice]:
        """Scan for nearby BLE devices using Bleak.

        Args:
            timeout: Scan duration in seconds (default: 5.0)

        Returns:
            List of discovered devices with their information

        """
        # Scan and get devices with advertisement data
        devices_and_adv_data = await BleakScanner.discover(timeout=timeout, return_adv=True)

        scanned_devices: list[ScannedDevice] = []

        for device, adv_data in devices_and_adv_data.values():
            # Parse the raw advertisement data if available
            advertisement_data = None
            if adv_data:
                # Create AdvertisingData from Bleak's AdvertisementData

                # Build CoreAdvertisingData from Bleak's data
                core_data = CoreAdvertisingData(
                    manufacturer_data=adv_data.manufacturer_data,
                    service_uuids=adv_data.service_uuids,
                    service_data=adv_data.service_data,
                    local_name=adv_data.local_name or "",
                )

                # Build DeviceProperties
                properties = DeviceProperties(
                    tx_power=adv_data.tx_power if adv_data.tx_power is not None else 0,
                )

                # Create the complete AdvertisingData structure
                advertisement_data = AdvertisingData(
                    raw_data=b"",  # Bleak doesn't expose raw PDU
                    ad_structures=AdvertisingDataStructures(
                        core=core_data,
                        properties=properties,
                    ),
                    rssi=adv_data.rssi,
                )

            scanned_device = ScannedDevice(
                address=device.address,
                name=device.name,
                advertisement_data=advertisement_data,
            )
            scanned_devices.append(scanned_device)

        return scanned_devices

    @property
    def mtu_size(self) -> int:
        """Get the current MTU (Maximum Transmission Unit) size.

        Returns:
            MTU size in bytes (typically 23-512)

        """
        return self.client.mtu_size

    @property
    def name(self) -> str:
        """Get the device name.

        Returns:
            Human-readable device name

        """
        return self.client.name

    @property
    def address(self) -> str:
        """Get the device address.

        Returns:
            Bluetooth MAC address or UUID (on macOS)

        """
        return self._address
