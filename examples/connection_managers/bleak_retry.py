"""Bleak-based connection manager for bluetooth-sig-python.

This module provides a Bleak backend implementation with retry support,
comprehensive scanning capabilities, and proper async patterns.
"""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import sys
from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Any

from bleak import BleakClient, BleakScanner
from bleak.args.bluez import AdvertisementDataType, OrPattern  # type: ignore[attr-defined]
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData as BleakAdvertisementData

from bluetooth_sig.device.client import ClientManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types import ManufacturerData
from bluetooth_sig.types.advertising.ad_structures import (
    AdvertisingDataStructures,
    CoreAdvertisingData,
    DeviceProperties,
)
from bluetooth_sig.types.advertising.result import AdvertisementData
from bluetooth_sig.types.data_types import CharacteristicInfo
from bluetooth_sig.types.device_types import (
    DeviceService,
    ScanFilter,
    ScannedDevice,
    ScanningMode,
)

if TYPE_CHECKING:
    from bluetooth_sig.types.device_types import ScanDetectionCallback
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods  # Implements full ClientManagerProtocol interface
class BleakRetryClientManager(ClientManagerProtocol):
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
        self._latest_advertisement: AdvertisementData | None = None
        self.client = self._create_client()

    def _create_client(self) -> BleakClient:
        """Create a BleakClient with current settings.

        Returns:
            Configured BleakClient instance

        """
        # Use the Bleak-style callback directly
        return BleakClient(self.address, timeout=self.timeout, disconnected_callback=self._bleak_callback)

    async def connect(self, *, timeout: float = 10.0) -> None:
        """Connect to the device with retry logic.

        Args:
            timeout: Connection timeout in seconds.

        """
        last_exception = None
        for attempt in range(self.max_attempts):
            try:
                await self.client.connect(timeout=timeout)
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
                characteristics: dict[str, BaseCharacteristic[Any]] = {}
                for char in bleak_service.characteristics:
                    char_uuid = BluetoothUUID(char.uuid)

                    # Convert Bleak properties to GattProperty flags
                    properties: list[GattProperty] = []
                    prop_map = {
                        "broadcast": GattProperty.BROADCAST,
                        "read": GattProperty.READ,
                        "write-without-response": GattProperty.WRITE_WITHOUT_RESPONSE,
                        "write": GattProperty.WRITE,
                        "notify": GattProperty.NOTIFY,
                        "indicate": GattProperty.INDICATE,
                        "authenticated-signed-writes": GattProperty.AUTHENTICATED_SIGNED_WRITES,
                        "extended-properties": GattProperty.EXTENDED_PROPERTIES,
                        "reliable-write": GattProperty.RELIABLE_WRITE,
                        "writable-auxiliaries": GattProperty.WRITABLE_AUXILIARIES,
                    }
                    for prop in char.properties:
                        if prop in prop_map:
                            properties.append(prop_map[prop])
                        else:
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
        """Read the RSSI (signal strength) during an active connection.

        Bleak does not provide a cross-platform API for reading RSSI during
        an active connection. Use get_advertisement_rssi() to get the RSSI
        from the last advertisement instead.

        Raises:
            NotImplementedError: Bleak doesn't support connection RSSI

        """
        raise NotImplementedError(
            "Bleak does not provide connection RSSI. Use get_advertisement_rssi() "
            "or get_latest_advertisement(refresh=True) to get RSSI from advertisements."
        )

    async def get_advertisement_rssi(self, refresh: bool = False) -> int | None:
        """Get the RSSI from advertisement data.

        Args:
            refresh: If True, perform an active scan to get fresh RSSI.
                    If False, return the cached RSSI from last advertisement.

        Returns:
            RSSI value in dBm, or None if no advertisement has been received

        """
        if refresh:
            await self.get_latest_advertisement(refresh=True)

        if self._latest_advertisement is not None:
            return self._latest_advertisement.rssi
        return None

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be called when the device disconnects.

        Args:
            callback: Function to call when device disconnects.

        Raises:
            NotImplementedError: Bleak requires disconnected_callback in __init__.
                                Use the disconnected_callback parameter when creating
                                the BleakRetryClientManager instead.

        """
        raise NotImplementedError(
            "Bleak requires disconnected_callback to be set during initialization. "
            "Pass it to the BleakRetryClientManager constructor instead."
        )

    async def get_latest_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        """Return the most recently received advertisement data.

        Args:
            refresh: If True, perform a short active scan to get fresh data.
                    If False, return the last cached advertisement.

        Returns:
            Latest AdvertisementData, or None if none received yet

        """
        if refresh:
            scanner = BleakScanner()
            await scanner.start()
            await asyncio.sleep(1.0)  # Short scan
            await scanner.stop()

            # Find our device in results
            for ble_device, adv in scanner.discovered_devices_and_advertisement_data.values():
                if ble_device.address.upper() == self._address.upper():
                    self._latest_advertisement = self.convert_advertisement(adv)
                    break

        return self._latest_advertisement

    @classmethod
    def convert_advertisement(cls, advertisement: object) -> AdvertisementData:
        """Convert Bleak's AdvertisementData to our AdvertisementData type.

        This method bridges Bleak's framework-specific advertisement data to our
        unified AdvertisementData type.

        Args:
            advertisement: Bleak's AdvertisementData from scan callback

        Returns:
            Unified AdvertisementData with ad_structures populated

        """
        bleak_adv: BleakAdvertisementData = advertisement  # type: ignore[assignment]

        # Build CoreAdvertisingData from Bleak's data
        # Convert string UUIDs to BluetoothUUID objects
        service_uuids = [BluetoothUUID(uuid) for uuid in (bleak_adv.service_uuids or [])]
        service_data = {BluetoothUUID(uuid): data for uuid, data in (bleak_adv.service_data or {}).items()}

        manufacturer_data_converted = {
            company_id: ManufacturerData.from_id_and_payload(company_id, payload)
            for company_id, payload in (bleak_adv.manufacturer_data or {}).items()
        }

        core_data = CoreAdvertisingData(
            manufacturer_data=manufacturer_data_converted,
            service_uuids=service_uuids,
            service_data=service_data,
            local_name=bleak_adv.local_name or "",
        )

        # Build DeviceProperties
        properties = DeviceProperties(
            tx_power=bleak_adv.tx_power if bleak_adv.tx_power is not None else 0,
        )

        # Create the complete AdvertisementData structure
        return AdvertisementData(
            ad_structures=AdvertisingDataStructures(
                core=core_data,
                properties=properties,
            ),
            rssi=bleak_adv.rssi,
        )

    @classmethod
    def _effective_scanning_mode(cls, mode: ScanningMode) -> ScanningMode:
        """Get effective scanning mode, handling platform limitations."""
        if mode == "passive" and sys.platform == "darwin":
            logger.warning("Passive scanning not supported on macOS, using active")
            return "active"
        return mode

    @classmethod
    def _bluez_args(cls, adapter: str | None, scanning_mode: ScanningMode = "active") -> dict[str, Any]:
        """Build BlueZ-specific scanner arguments.

        For passive scanning on BlueZ, or_patterns are required. We provide a
        catch-all pattern that matches any advertisement with Flags AD type.
        """
        args: dict[str, Any] = {}
        if adapter:
            args["adapter"] = adapter

        # BlueZ requires or_patterns for passive scanning
        # Use a catch-all pattern matching Flags (0x01) which is in most advertisements
        if scanning_mode == "passive":
            # Match any advertisement with a Flags byte (position 0, any value)
            # Using empty bytes matches any content at that position
            catch_all_pattern = OrPattern(
                start_position=0,
                ad_data_type=AdvertisementDataType.FLAGS,
                content_of_pattern=b"",  # Empty matches any flags value
            )
            args["or_patterns"] = [catch_all_pattern]

        return args

    @classmethod
    def _to_scanned_device(cls, device: BLEDevice, adv: BleakAdvertisementData | None) -> ScannedDevice:
        """Convert Bleak device and advertisement to ScannedDevice."""
        return ScannedDevice(
            address=device.address,
            name=device.name,
            advertisement_data=cls.convert_advertisement(adv) if adv else None,
        )

    @classmethod
    async def scan(  # pylint: disable=too-many-arguments
        cls,
        timeout: float = 5.0,
        *,
        filters: ScanFilter | None = None,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
        callback: ScanDetectionCallback | None = None,
    ) -> list[ScannedDevice]:
        """Scan for nearby BLE devices.

        Args:
            timeout: Scan duration in seconds
            filters: Optional filter criteria
            scanning_mode: 'active' or 'passive' (passive unsupported on macOS)
            adapter: Bluetooth adapter (e.g., "hci0" on Linux)
            callback: Optional async/sync function called for each discovered device

        Returns:
            List of discovered devices matching filters

        """
        if callback:
            # Use callback-based scanning for real-time notifications
            return await cls._scan_with_callback(
                callback=callback,
                timeout=timeout,
                filters=filters,
                scanning_mode=scanning_mode,
                adapter=adapter,
            )

        # Standard batch scanning
        effective_mode = cls._effective_scanning_mode(scanning_mode)
        service_uuids = filters.service_uuids if filters else None
        bluez = cls._bluez_args(adapter, effective_mode)

        # Bleak's discover returns dict when return_adv=True
        if service_uuids:
            results = await BleakScanner.discover(  # type: ignore[call-overload]
                timeout=timeout,
                return_adv=True,
                service_uuids=service_uuids,
                scanning_mode=effective_mode,
                bluez=bluez,
            )
        else:
            results = await BleakScanner.discover(  # type: ignore[call-overload]
                timeout=timeout,
                return_adv=True,
                scanning_mode=effective_mode,
                bluez=bluez,
            )

        devices: list[ScannedDevice] = []
        for device, adv in results.values():
            scanned = cls._to_scanned_device(device, adv)

            # Apply remaining filters (service_uuids already applied at OS level)
            if filters:
                post_filter = ScanFilter(
                    addresses=filters.addresses,
                    names=filters.names,
                    rssi_threshold=filters.rssi_threshold,
                    filter_func=filters.filter_func,
                )
                if not post_filter.matches(scanned):
                    continue

            devices.append(scanned)

        return devices

    @classmethod
    async def _scan_with_callback(  # pylint: disable=too-many-arguments
        cls,
        callback: ScanDetectionCallback,
        timeout: float | None = 5.0,
        *,
        filters: ScanFilter | None = None,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> list[ScannedDevice]:
        """Internal: Scan with real-time callbacks as devices are discovered."""
        discovered: dict[str, ScannedDevice] = {}
        effective_mode = cls._effective_scanning_mode(scanning_mode)
        bluez = cls._bluez_args(adapter, effective_mode)
        service_uuids = filters.service_uuids if filters else None

        def on_detection(device: BLEDevice, adv: BleakAdvertisementData) -> None:
            scanned = cls._to_scanned_device(device, adv)

            if filters and not filters.matches(scanned):
                return

            discovered[device.address] = scanned

            result = callback(scanned)
            if inspect.isawaitable(result):
                asyncio.create_task(result)  # type: ignore[arg-type]

        scanner = BleakScanner(
            detection_callback=on_detection,
            service_uuids=service_uuids,
            scanning_mode=effective_mode,
            bluez=bluez,  # type: ignore[arg-type]
        )

        await scanner.start()
        if timeout is not None:
            await asyncio.sleep(timeout)
        else:
            try:
                await asyncio.Future()  # type: ignore[arg-type]
            except asyncio.CancelledError:
                pass
        await scanner.stop()

        return list(discovered.values())

    @classmethod
    async def find_device(  # pylint: disable=too-many-return-statements
        cls,
        filters: ScanFilter,
        timeout: float = 10.0,
        *,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> ScannedDevice | None:
        """Find the first device matching filter criteria.

        Uses Bleak's native early-termination for efficiency when possible.

        Args:
            filters: Filter criteria (address, name, service_uuids, or filter_func)
            timeout: Maximum scan time in seconds
            scanning_mode: 'active' or 'passive'
            adapter: Bluetooth adapter to use

        Returns:
            First matching device or None

        """
        effective_mode = cls._effective_scanning_mode(scanning_mode)
        bluez = cls._bluez_args(adapter, effective_mode)

        # Use Bleak's native find methods when applicable for early termination
        if filters.addresses and len(filters.addresses) == 1 and not filters.names and not filters.filter_func:
            # Single address lookup - use Bleak's native method
            ble_device = await BleakScanner.find_device_by_address(
                filters.addresses[0],
                timeout=timeout,
                bluez=bluez,  # type: ignore[arg-type]
            )
            if not ble_device:
                return None
            adv = await cls._get_advertisement_for_device(ble_device.address, bluez, timeout)
            return cls._to_scanned_device(ble_device, adv)

        if filters.names and len(filters.names) == 1 and not filters.addresses and not filters.filter_func:
            # Single name lookup - use Bleak's native method
            ble_device = await BleakScanner.find_device_by_name(
                filters.names[0],
                timeout=timeout,
                bluez=bluez,  # type: ignore[arg-type]
            )
            if not ble_device:
                return None
            adv = await cls._get_advertisement_for_device(ble_device.address, bluez, timeout)
            return cls._to_scanned_device(ble_device, adv)

        if filters.filter_func and not filters.addresses and not filters.names:
            # Custom filter - use Bleak's native filter method
            def bleak_filter(device: BLEDevice, adv: BleakAdvertisementData) -> bool:
                scanned = cls._to_scanned_device(device, adv)
                return filters.matches(scanned)

            ble_device = await BleakScanner.find_device_by_filter(
                bleak_filter,
                timeout=timeout,
                bluez=bluez,  # type: ignore[arg-type]
            )
            if not ble_device:
                return None
            adv = await cls._get_advertisement_for_device(ble_device.address, bluez, timeout)
            return cls._to_scanned_device(ble_device, adv)

        # Fallback: full scan and return first match
        devices = await cls.scan(
            timeout=timeout,
            filters=filters,
            scanning_mode=scanning_mode,
            adapter=adapter,
        )
        return devices[0] if devices else None

    @classmethod
    async def _get_advertisement_for_device(
        cls,
        address: str,
        bluez: dict[str, Any],
        timeout: float,
    ) -> BleakAdvertisementData | None:
        """Helper to get advertisement data for a known device."""
        scanner = BleakScanner(bluez=bluez)  # type: ignore[arg-type]
        await scanner.start()
        await asyncio.sleep(min(1.0, timeout / 4))
        await scanner.stop()

        for dev, adv in scanner.discovered_devices_and_advertisement_data.values():
            if dev.address.upper() == address.upper():
                return adv
        return None

    @classmethod
    async def _scan_stream_impl(
        cls,
        timeout: float | None,
        filters: ScanFilter | None,
        scanning_mode: ScanningMode,
        adapter: str | None,
    ) -> AsyncIterator[ScannedDevice]:
        """Async generator yielding devices as discovered."""
        queue: asyncio.Queue[ScannedDevice | None] = asyncio.Queue()
        seen: set[str] = set()
        effective_mode = cls._effective_scanning_mode(scanning_mode)
        bluez = cls._bluez_args(adapter, effective_mode)
        service_uuids = filters.service_uuids if filters else None

        def on_detection(device: BLEDevice, adv: BleakAdvertisementData) -> None:
            if device.address in seen:
                return

            scanned = cls._to_scanned_device(device, adv)
            if filters and not filters.matches(scanned):
                return

            seen.add(device.address)
            queue.put_nowait(scanned)

        scanner = BleakScanner(
            detection_callback=on_detection,
            service_uuids=service_uuids,
            scanning_mode=effective_mode,
            bluez=bluez,  # type: ignore[arg-type]
        )

        async def scan_task() -> None:
            await scanner.start()
            if timeout is not None:
                await asyncio.sleep(timeout)
            else:
                await asyncio.Future()  # type: ignore[arg-type]
            await scanner.stop()
            queue.put_nowait(None)

        task = asyncio.create_task(scan_task())

        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            await scanner.stop()

    @classmethod
    def scan_stream(
        cls,
        timeout: float | None = 5.0,
        *,
        filters: ScanFilter | None = None,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> AsyncIterator[ScannedDevice]:
        """Stream discovered devices as an async iterator.

        Enables early termination by breaking from the loop.

        Args:
            timeout: Scan duration (None for indefinite)
            filters: Optional filter criteria
            scanning_mode: 'active' or 'passive'
            adapter: Bluetooth adapter to use.

        Yields:
            ScannedDevice objects as they are discovered

        Example::

            async for device in BleakRetryClientManager.scan_stream(timeout=10.0):
                print(f"Found: {device.name}")
                if device.name == "My Target Device":
                    break  # Stop scanning early

        """
        return cls._scan_stream_impl(
            timeout=timeout,
            filters=filters,
            scanning_mode=scanning_mode,
            adapter=adapter,
        )

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
