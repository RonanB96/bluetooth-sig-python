"""BluePy-based connection manager for BLE devices.

This module provides a connection manager implementation using BluePy,
following the same pattern as Bleak and SimplePyBLE managers.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Callable, ClassVar

from bluepy.btle import (
    ADDR_TYPE_RANDOM,
    UUID,
    BTLEException,
    Characteristic,
    Peripheral,
    ScanEntry,
    Scanner,
    Service,
)

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types import ManufacturerData
from bluetooth_sig.types.ad_types_constants import ADType
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


# pylint: disable=too-many-public-methods  # Implements ConnectionManagerProtocol interface
class BluePyConnectionManager(ConnectionManagerProtocol):
    """Connection manager using BluePy for BLE communication.

    Implements ConnectionManagerProtocol to integrate BluePy with
    the bluetooth-sig-python Device class.
    """

    supports_scanning: ClassVar[bool] = True

    def __init__(self, address: str, addr_type: str = ADDR_TYPE_RANDOM, timeout: float = 20.0) -> None:
        """Initialize the connection manager.

        Args:
            address: BLE MAC address
            addr_type: Address type (ADDR_TYPE_RANDOM or ADDR_TYPE_PUBLIC)
            timeout: Connection timeout in seconds

        """
        super().__init__(address)
        self.addr_type = addr_type
        self.timeout = timeout
        self.periph: Peripheral | None = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._cached_services: list[DeviceService] | None = None
        self._latest_advertisement: AdvertisementData | None = None

    @staticmethod
    def to_bluepy_uuid(uuid: BluetoothUUID) -> UUID:
        """Convert BluetoothUUID to BluePy UUID.

        Args:
            uuid: BluetoothUUID instance

        Returns:
            Corresponding BluePy UUID instance
        """
        return UUID(str(uuid))

    @staticmethod
    def to_bluetooth_uuid(uuid: UUID) -> BluetoothUUID:
        """Convert BluePy UUID to BluetoothUUID.

        Args:
            uuid: BluePy UUID instance

        Returns:
            Corresponding BluetoothUUID instance
        """
        return BluetoothUUID(str(uuid))

    async def connect(self, *, timeout: float = 10.0) -> None:
        """Connect to device.

        Args:
            timeout: Connection timeout in seconds.

        """

        def _connect() -> None:
            try:
                # Peripheral() doesn't support timeout parameter directly, but connection
                # timeout is handled at the Bluetooth stack level
                self.periph = Peripheral(self.address, addrType=self.addr_type)
                self._cached_services = None  # Clear cache on new connection
            except BTLEException as e:
                if "Failed to connect to peripheral" in str(e):
                    # First attempt failed, try with public address type
                    try:
                        self.periph = Peripheral(self.address, addrType="public")
                        self._cached_services = None  # Clear cache on new connection
                    except BTLEException as e2:
                        raise RuntimeError(
                            f"Failed to connect to {self.address} with both random and public address types: {e2}"
                        ) from e2
                else:
                    raise RuntimeError(f"Failed to connect to {self.address}: {e}") from e

        # Use timeout with run_in_executor
        try:
            await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(self.executor, _connect), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Connection to {self.address} timed out after {timeout}s") from None

    async def disconnect(self) -> None:
        """Disconnect from device."""

        def _disconnect() -> None:
            if self.periph:
                self.periph.disconnect()
                self.periph = None
                self._cached_services = None  # Clear cache on disconnect

        await asyncio.get_event_loop().run_in_executor(self.executor, _disconnect)

    @property
    def is_connected(self) -> bool:
        """Check if connected.

        Returns:
            True if connected.

        """
        return self.periph is not None

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read GATT characteristic.

        Args:
            char_uuid: Characteristic UUID.

        Returns:
            Raw characteristic bytes.

        Raises:
            RuntimeError: If not connected or read fails.

        """

        def _read() -> bytes:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                characteristics: list[Characteristic] = self.periph.getCharacteristics(
                    uuid=self.to_bluepy_uuid(char_uuid)
                )  # type: ignore[misc]
                if not characteristics:
                    raise RuntimeError(f"Characteristic {char_uuid} not found")

                # First (and typically only) characteristic with this UUID
                char: Characteristic = characteristics[0]
                return char.read()  # type: ignore[no-any-return]
            except BTLEException as e:
                raise RuntimeError(f"BluePy error reading characteristic {char_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to read characteristic {char_uuid}: {e}") from e

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        """Write GATT characteristic.

        Args:
            char_uuid: Characteristic UUID
            data: Data to write
            response: If True, use write-with-response; if False, use write-without-response

        Raises:
            RuntimeError: If not connected or write fails
        """

        def _write() -> None:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                characteristics: list[Characteristic] = self.periph.getCharacteristics(
                    uuid=self.to_bluepy_uuid(char_uuid)
                )  # type: ignore[misc]
                if not characteristics:
                    raise RuntimeError(f"Characteristic {char_uuid} not found")

                # First (and typically only) characteristic with this UUID
                char: Characteristic = characteristics[0]
                _ = char.write(data, withResponse=response)  # type: ignore[misc]
                # BluePy write returns a response dict - we don't need to check it specifically
                # as BluePy will raise an exception if the write fails
            except BTLEException as e:
                raise RuntimeError(f"BluePy error writing characteristic {char_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to write characteristic {char_uuid}: {e}") from e

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> list[DeviceService]:
        """Get services from device.

        Services are cached after first retrieval. BluePy's getServices() performs
        service discovery each call, so caching is important for efficiency.

        Returns:
            List of DeviceService objects converted from BluePy services
        """
        # Return cached services if available
        if self._cached_services is not None:
            return self._cached_services

        def _get_services() -> list[DeviceService]:
            if not self.periph:
                raise RuntimeError("Not connected")

            # BluePy's getServices() performs discovery - cache the result
            bluepy_services: list[Service] = list(self.periph.getServices())  # type: ignore[misc]

            device_services: list[DeviceService] = []
            for bluepy_service in bluepy_services:
                service_uuid = self.to_bluetooth_uuid(bluepy_service.uuid)
                service_class = GattServiceRegistry.get_service_class(service_uuid)

                if service_class:
                    service_instance = service_class()

                    # Populate characteristics with actual class instances
                    characteristics: dict[str, BaseCharacteristic[Any]] = {}
                    for char in bluepy_service.getCharacteristics():  # type: ignore[misc]
                        char_uuid = self.to_bluetooth_uuid(char.uuid)

                        # Extract properties from BluePy characteristic
                        properties: list[GattProperty] = []
                        if hasattr(char, "properties") and char.properties:
                            # BluePy stores properties as an integer bitmask
                            prop_flags = char.properties
                            # Bit flags from Bluetooth spec
                            if prop_flags & 0x02:  # Read
                                properties.append(GattProperty.READ)
                            if prop_flags & 0x04:  # Write without response
                                properties.append(GattProperty.WRITE_WITHOUT_RESPONSE)
                            if prop_flags & 0x08:  # Write
                                properties.append(GattProperty.WRITE)
                            if prop_flags & 0x10:  # Notify
                                properties.append(GattProperty.NOTIFY)
                            if prop_flags & 0x20:  # Indicate
                                properties.append(GattProperty.INDICATE)

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
                                name=f"Unknown Characteristic ({char_uuid.short_form}...)",
                            )
                            char_instance = UnknownCharacteristic(info=char_info, properties=properties)
                            characteristics[str(char_uuid)] = char_instance

                    # Type ignore needed due to dict invariance with union types
                    device_services.append(DeviceService(service=service_instance, characteristics=characteristics))  # type: ignore[arg-type]

            return device_services

        result = await asyncio.get_event_loop().run_in_executor(self.executor, _get_services)

        # Cache the result
        self._cached_services = result
        return result

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
            callback: Notification callback
        """
        raise NotImplementedError("Notifications not implemented in this example")

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
        """
        raise NotImplementedError("Notifications not implemented in this example")

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        """Read GATT descriptor.

        Args:
            desc_uuid: Descriptor UUID

        Returns:
            Raw descriptor bytes

        Raises:
            RuntimeError: If not connected or read fails
        """

        def _read_descriptor() -> bytes:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                descriptors = self.periph.getDescriptors()  # type: ignore[misc]
                for desc in descriptors:
                    if str(desc.uuid).lower() == str(desc_uuid).lower():
                        return desc.read()  # type: ignore[no-any-return]
                raise RuntimeError(f"Descriptor {desc_uuid} not found")
            except BTLEException as e:
                raise RuntimeError(f"BluePy error reading descriptor {desc_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to read descriptor {desc_uuid}: {e}") from e

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read_descriptor)

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        """Write GATT descriptor.

        Args:
            desc_uuid: Descriptor UUID
            data: Data to write

        Raises:
            RuntimeError: If not connected or write fails
        """

        def _write_descriptor() -> None:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                descriptors = self.periph.getDescriptors()  # type: ignore[misc]
                for desc in descriptors:
                    if str(desc.uuid).lower() == str(desc_uuid).lower():
                        desc.write(data)  # type: ignore[misc]
                        return
                raise RuntimeError(f"Descriptor {desc_uuid} not found")
            except BTLEException as e:
                raise RuntimeError(f"BluePy error writing descriptor {desc_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to write descriptor {desc_uuid}: {e}") from e

        await asyncio.get_event_loop().run_in_executor(self.executor, _write_descriptor)

    async def pair(self) -> None:
        """Pair with the device.

        Raises:
            NotImplementedError: BluePy doesn't have explicit pairing API

        """
        raise NotImplementedError("Pairing not supported in BluePy connection manager")

    async def unpair(self) -> None:
        """Unpair from the device.

        Raises:
            NotImplementedError: BluePy doesn't have explicit unpairing API

        """
        raise NotImplementedError("Unpairing not supported in BluePy connection manager")

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) during an active connection.

        Raises:
            NotImplementedError: BluePy doesn't support reading RSSI from connected devices

        Note:
            BluePy only provides RSSI values during scanning (from advertising packets).
            Once connected, there's no API to read RSSI from an active connection.
            Use get_advertisement_rssi() to get the last advertised RSSI.
            See: https://github.com/IanHarvey/bluepy/issues/394

        """
        raise NotImplementedError(
            "BluePy does not support connection RSSI. Use get_advertisement_rssi() "
            "to get RSSI from the last advertisement."
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
            callback: Function to call when device disconnects

        Raises:
            NotImplementedError: BluePy doesn't provide disconnection callbacks
        """
        raise NotImplementedError("Disconnection callbacks not supported in BluePy connection manager")

    @property
    def mtu_size(self) -> int:
        """Get the current MTU (Maximum Transmission Unit) size.

        Returns:
            MTU size in bytes (typically 23-512)

        Raises:
            NotImplementedError: BluePy doesn't expose MTU information
        """
        raise NotImplementedError("MTU size not supported in BluePy connection manager")

    @property
    def address(self) -> str:
        """Get the device's Bluetooth address.

        Returns:
            Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        """
        if self.periph:
            return self.periph.addr  # type: ignore[no-any-return]
        return self._address  # Fall back to stored address if not connected

    @property
    def name(self) -> str:
        """Get the device name.

        Returns:
            Device name or "Unknown" if not available

        Note:
            BluePy doesn't provide a direct name property. Reading the GAP
            Device Name characteristic (0x2A00) would require service discovery.
            This returns "Unknown" for simplicity.

        """
        return "Unknown"

    async def get_latest_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        """Return the most recently received advertisement data.

        Args:
            refresh: If True, perform a short active scan to get fresh data.
                    If False, return the last cached advertisement.

        Returns:
            Latest AdvertisementData, or None if none received yet

        """
        if refresh:

            def _do_scan() -> AdvertisementData | None:
                scanner = Scanner()
                entries = scanner.scan(1.0)  # 1 second scan
                for entry in entries:
                    if entry.addr.upper() == self._address.upper():
                        return self.convert_advertisement(entry)
                return None

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, _do_scan)
            if result is not None:
                self._latest_advertisement = result

        return self._latest_advertisement

    @classmethod
    def convert_advertisement(cls, advertisement: object) -> AdvertisementData:
        """Convert BluePy scan entry to our AdvertisementData type.

        BluePy provides advertisement data through ScanEntry objects during scanning.
        This method extracts the relevant fields using ADType constants.

        Args:
            advertisement: BluePy ScanEntry object from scan results

        Returns:
            Unified AdvertisementData with ad_structures populated

        Note:
            BluePy's getScanData() returns (ad_type, desc, hex_value) tuples.
            Values are hex strings that need conversion to bytes.

        """
        # Constants for data parsing
        _COMPANY_ID_LENGTH = 2
        _SERVICE_UUID16_LENGTH = 2

        manufacturer_data: dict[int, bytes] = {}
        service_uuids: list[str] = []
        service_data: dict[BluetoothUUID, bytes] = {}
        local_name: str = ""
        tx_power: int = 0

        scan_data = advertisement.getScanData()  # type: ignore[attr-defined]
        for ad_type, _desc, value in scan_data:
            # Convert hex string to bytes - some values may not be hex encoded
            try:
                ad_bytes = bytes.fromhex(value) if value else b""
            except ValueError:
                # Value is not a hex string (e.g., device name as plain text)
                ad_bytes = value.encode("utf-8") if isinstance(value, str) else b""

            # Device names
            if ad_type == ADType.COMPLETE_LOCAL_NAME or (ad_type == ADType.SHORTENED_LOCAL_NAME and not local_name):
                local_name = ad_bytes.decode("utf-8", errors="replace")

            # Manufacturer data (first 2 bytes are company ID, little-endian)
            elif ad_type == ADType.MANUFACTURER_SPECIFIC_DATA and len(ad_bytes) >= _COMPANY_ID_LENGTH:
                company_id = int.from_bytes(ad_bytes[:_COMPANY_ID_LENGTH], byteorder="little")
                manufacturer_data[company_id] = ad_bytes[_COMPANY_ID_LENGTH:]

            # 16-bit Service UUIDs
            elif ad_type in (ADType.INCOMPLETE_16BIT_SERVICE_UUIDS, ADType.COMPLETE_16BIT_SERVICE_UUIDS):
                for i in range(0, len(ad_bytes), 2):
                    if i + 1 < len(ad_bytes):
                        uuid16 = int.from_bytes(ad_bytes[i : i + 2], byteorder="little")
                        service_uuids.append(f"{uuid16:04X}")

            # 32-bit Service UUIDs
            elif ad_type in (ADType.INCOMPLETE_32BIT_SERVICE_UUIDS, ADType.COMPLETE_32BIT_SERVICE_UUIDS):
                for i in range(0, len(ad_bytes), 4):
                    if i + 3 < len(ad_bytes):
                        uuid32 = int.from_bytes(ad_bytes[i : i + 4], byteorder="little")
                        service_uuids.append(f"{uuid32:08X}")

            # 128-bit Service UUIDs
            elif ad_type in (ADType.INCOMPLETE_128BIT_SERVICE_UUIDS, ADType.COMPLETE_128BIT_SERVICE_UUIDS):
                for i in range(0, len(ad_bytes), 16):
                    if i + 15 < len(ad_bytes):
                        uuid_bytes = ad_bytes[i : i + 16][::-1]  # Reverse for standard format
                        uuid_hex = uuid_bytes.hex().upper()
                        # Format as standard UUID: 8-4-4-4-12
                        formatted = (
                            f"{uuid_hex[:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:]}"
                        )
                        service_uuids.append(formatted)

            # 16-bit Service Data
            elif ad_type == ADType.SERVICE_DATA_16BIT and len(ad_bytes) >= _SERVICE_UUID16_LENGTH:
                uuid16 = int.from_bytes(ad_bytes[:_SERVICE_UUID16_LENGTH], byteorder="little")
                service_data[BluetoothUUID(f"{uuid16:04X}")] = ad_bytes[_SERVICE_UUID16_LENGTH:]

            # TX Power Level
            elif ad_type == ADType.TX_POWER_LEVEL and len(ad_bytes) >= 1:
                tx_power = int.from_bytes(ad_bytes[:1], byteorder="little", signed=True)

        manufacturer_data_converted = {
            company_id: ManufacturerData.from_id_and_payload(company_id, payload)
            for company_id, payload in manufacturer_data.items()
        }

        core_data = CoreAdvertisingData(
            manufacturer_data=manufacturer_data_converted,
            service_uuids=[BluetoothUUID(uuid) for uuid in service_uuids],
            service_data=service_data,
            local_name=local_name,
        )

        properties = DeviceProperties(
            tx_power=tx_power,
        )

        return AdvertisementData(
            ad_structures=AdvertisingDataStructures(
                core=core_data,
                properties=properties,
            ),
            rssi=advertisement.rssi,  # type: ignore[attr-defined]
        )

    # =========================================================================
    # SCANNING METHODS
    # =========================================================================

    @classmethod
    def _scan_entry_to_scanned_device(cls, entry: ScanEntry) -> ScannedDevice:
        """Convert a BluePy ScanEntry to a ScannedDevice."""
        return ScannedDevice(
            address=entry.addr,
            name=entry.getValueText(9) or None,  # 9 = Complete Local Name
            advertisement_data=cls.convert_advertisement(entry),
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
            scanning_mode: 'active' or 'passive'
            adapter: Ignored (BluePy uses default adapter)
            callback: Optional async/sync function called for each discovered device

        Returns:
            List of discovered devices matching filters

        Raises:
            PermissionError: If not running with root/sudo privileges

        """
        del adapter  # Unused - BluePy uses default adapter
        loop = asyncio.get_event_loop()
        passive = scanning_mode == "passive"

        def _scan() -> list[ScanEntry]:
            scanner = Scanner()
            try:
                return list(scanner.scan(timeout, passive=passive))
            except BTLEException as e:
                if "Failed to execute management command" in str(e):
                    raise PermissionError(
                        "BluePy scanning requires root privileges. Run with: sudo python <script>"
                    ) from e
                raise

        entries = await loop.run_in_executor(None, _scan)

        devices: list[ScannedDevice] = []
        for entry in entries:
            scanned = cls._scan_entry_to_scanned_device(entry)
            if filters and not filters.matches(scanned):
                continue
            devices.append(scanned)
            if callback:
                result = callback(scanned)
                if inspect.isawaitable(result):
                    await result

        return devices

    @classmethod
    async def find_device(
        cls,
        filters: ScanFilter,
        timeout: float = 10.0,
        *,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> ScannedDevice | None:
        """Find the first device matching filter criteria.

        Args:
            filters: Filter criteria (address, name, service_uuids, or filter_func)
            timeout: Maximum scan time in seconds
            scanning_mode: 'active' or 'passive'
            adapter: Ignored

        Returns:
            First matching device or None

        """
        del adapter  # Unused
        devices = await cls.scan(timeout=timeout, filters=filters, scanning_mode=scanning_mode)
        return devices[0] if devices else None

    @classmethod
    def scan_stream(
        cls,
        timeout: float | None = 10.0,
        *,
        filters: ScanFilter | None = None,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> AsyncIterator[ScannedDevice]:
        """Stream discovered devices as an async iterator.

        Note: BluePy doesn't support true streaming, so this
        scans first then yields devices.

        Args:
            timeout: Scan duration in seconds
            filters: Optional filter criteria
            scanning_mode: 'active' or 'passive'
            adapter: Ignored

        Yields:
            ScannedDevice for each discovered device

        """
        del adapter  # Unused

        async def _stream() -> AsyncIterator[ScannedDevice]:
            scan_timeout = timeout if timeout is not None else 10.0
            devices = await cls.scan(timeout=scan_timeout, filters=filters, scanning_mode=scanning_mode)
            for device in devices:
                yield device

        return _stream()
