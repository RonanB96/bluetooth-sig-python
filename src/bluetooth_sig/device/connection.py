"""Connection manager protocol for BLE transport adapters.

Defines an async abstract base class that adapter implementations (Bleak,
SimplePyBLE, etc.) must inherit from so the `Device` class can operate
independently of the underlying BLE library.

Adapters must provide async implementations of all abstract methods below.
For sync-only libraries an adapter can run sync calls in a thread and
expose an async interface.
"""
# pylint: disable=duplicate-code  # Pattern repetition is expected for protocol definitions
# pylint: disable=too-many-public-methods  # BLE connection protocol requires complete interface

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Callable, ClassVar

from bluetooth_sig.types.advertising import AdvertisementData
from bluetooth_sig.types.device_types import (
    DeviceService,
    ScanFilter,
    ScannedDevice,
    ScanningMode,
)
from bluetooth_sig.types.uuid import BluetoothUUID

if TYPE_CHECKING:
    from bluetooth_sig.types.device_types import ScanDetectionCallback


class ConnectionManagerProtocol(ABC):
    """Abstract base class describing the transport operations Device expects.

    All methods are async so adapters can integrate naturally with async
    libraries like Bleak. Synchronous libraries must be wrapped by adapters
    to provide async interfaces.

    Subclasses MUST implement all abstract methods and properties.
    """

    # Class-level flag to indicate if this backend supports scanning
    supports_scanning: ClassVar[bool] = False

    def __init__(self, address: str) -> None:
        """Initialize the connection manager.

        Args:
            address: The Bluetooth device address (MAC address)

        """
        self._address = address

    @property
    def address(self) -> str:
        """Get the device address.

        Returns:
            Bluetooth device address (MAC address)

        Note:
            Subclasses may override this to provide address from underlying library.

        """
        return self._address

    @abstractmethod
    async def connect(self) -> None:
        """Open a connection to the device."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the device."""

    @abstractmethod
    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read the raw bytes of a characteristic identified by `char_uuid`."""

    @abstractmethod
    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        """Write raw bytes to a characteristic identified by `char_uuid`.

        Args:
            char_uuid: The UUID of the characteristic to write to
            data: The raw bytes to write
            response: If True, use write-with-response (wait for acknowledgment).
                     If False, use write-without-response (faster but no confirmation).
                     Default is True for reliability.

        """

    @abstractmethod
    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        """Read the raw bytes of a descriptor identified by `desc_uuid`.

        Args:
            desc_uuid: The UUID of the descriptor to read

        Returns:
            The raw descriptor data as bytes

        """

    @abstractmethod
    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        """Write raw bytes to a descriptor identified by `desc_uuid`.

        Args:
            desc_uuid: The UUID of the descriptor to write to
            data: The raw bytes to write

        """

    @abstractmethod
    async def get_services(self) -> list[DeviceService]:
        """Return a structure describing services/characteristics from the adapter.

        The concrete return type depends on the adapter; `Device` uses
        this only for enumeration in examples. Adapters should provide
        iterable objects with `.characteristics` elements that have
        `.uuid` and `.properties` attributes, or the adapter can return
        a mapping.
        """

    @abstractmethod
    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications for `char_uuid` and invoke `callback(uuid, data)` on updates."""

    @abstractmethod
    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications for `char_uuid`."""

    @abstractmethod
    async def pair(self) -> None:
        """Pair with the device.

        Raises an exception if pairing fails.

        Note:
            On macOS, pairing is automatic when accessing authenticated characteristics.
            This method may not be needed on that platform.

        """

    @abstractmethod
    async def unpair(self) -> None:
        """Unpair from the device.

        Raises an exception if unpairing fails.

        """

    @abstractmethod
    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) during an active connection.

        This reads RSSI from the active BLE connection. Not all backends
        support this - some only provide RSSI from advertisement data.

        Returns:
            RSSI value in dBm (typically negative, e.g., -60)

        Raises:
            NotImplementedError: If this backend doesn't support connection RSSI
            RuntimeError: If not connected

        """

    @abstractmethod
    async def get_advertisement_rssi(self, refresh: bool = False) -> int | None:
        """Get the RSSI from advertisement data.

        This returns the RSSI from advertisement data. Does not require
        an active connection.

        Args:
            refresh: If True, perform an active scan to get fresh RSSI.
                    If False, return the cached RSSI from last advertisement.

        Returns:
            RSSI value in dBm, or None if no advertisement has been received

        """

    @abstractmethod
    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be invoked when the device disconnects.

        Args:
            callback: Function to call when disconnection occurs

        """

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the connection is currently active.

        Returns:
            True if connected to the device, False otherwise

        """

    @property
    @abstractmethod
    def mtu_size(self) -> int:
        """Get the negotiated MTU size in bytes.

        Returns:
            The MTU size negotiated for this connection (typically 23-512 bytes)

        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the device.

        Returns:
            The name of the device as a string

        """

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

        This is a class method that doesn't require an instance. Not all backends
        support scanning - check the `supports_scanning` class attribute.

        Args:
            timeout: Scan duration in seconds (default: 5.0)
            filters: Optional filter criteria. Devices not matching filters are excluded.
                Filtering may happen at OS level (more efficient) or post-scan depending
                on backend capabilities.
            scanning_mode: 'active' (default) sends scan requests for scan response data,
                'passive' only listens to advertisements (saves power, faster).
                Note: Passive scanning is NOT supported on macOS.
            adapter: Backend-specific adapter identifier (e.g., "hci0" for BlueZ).
                None uses the default adapter.
            callback: Optional async or sync function called with each ScannedDevice
                as it's discovered. Enables real-time UI updates and early processing.
                If async, it's awaited before continuing.

        Returns:
            List of discovered devices matching the filters

        Raises:
            NotImplementedError: If this backend doesn't support scanning

        Example::

            # Basic scan
            devices = await MyConnectionManager.scan(timeout=5.0)

            # Filtered scan for Heart Rate monitors
            from bluetooth_sig.types.device_types import ScanFilter

            filters = ScanFilter(service_uuids=["180d"], rssi_threshold=-70)
            devices = await MyConnectionManager.scan(timeout=10.0, filters=filters)


            # Scan with real-time callback
            async def on_device(device: ScannedDevice) -> None:
                print(f"Found: {device.name or device.address}")


            devices = await MyConnectionManager.scan(timeout=10.0, callback=on_device)

        """
        raise NotImplementedError(f"{cls.__name__} does not support scanning")

    @classmethod
    async def find_device(
        cls,
        filters: ScanFilter,
        timeout: float = 10.0,
        *,
        scanning_mode: ScanningMode = "active",
        adapter: str | None = None,
    ) -> ScannedDevice | None:
        """Find the first device matching the filter criteria.

        This is more efficient than a full scan when looking for a specific device.
        Use ScanFilter to match by address, name, service UUIDs, or custom function.

        Args:
            filters: Filter criteria. Use ScanFilter(addresses=[...]) for address,
                ScanFilter(names=[...]) for name, or ScanFilter(filter_func=...) for
                custom matching logic.
            timeout: Maximum time to scan in seconds (default: 10.0)
            scanning_mode: 'active' or 'passive' scanning mode.
            adapter: Backend-specific adapter identifier. None uses default.

        Returns:
            The first matching device, or None if not found within timeout

        Raises:
            NotImplementedError: If this backend doesn't support scanning

        Example::

            # Find by address
            device = await MyConnectionManager.find_device(
                ScanFilter(addresses=["AA:BB:CC:DD:EE:FF"]),
                timeout=15.0,
            )

            # Find by name
            device = await MyConnectionManager.find_device(
                ScanFilter(names=["Polar H10"]),
                timeout=15.0,
            )


            # Find with custom filter
            def has_apple_data(device: ScannedDevice) -> bool:
                if device.advertisement_data is None:
                    return False
                mfr = device.advertisement_data.ad_structures.core.manufacturer_data
                return 0x004C in mfr


            device = await MyConnectionManager.find_device(
                ScanFilter(filter_func=has_apple_data),
                timeout=10.0,
            )

        """
        raise NotImplementedError(f"{cls.__name__} does not support find_device")

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

        This provides the most Pythonic way to process devices as they're
        discovered, with full async/await support and easy early termination.

        Args:
            timeout: Scan duration in seconds. None for indefinite.
            filters: Optional filter criteria.
            scanning_mode: 'active' or 'passive'.
            adapter: Backend-specific adapter identifier.

        Yields:
            ScannedDevice objects as they are discovered

        Raises:
            NotImplementedError: If this backend doesn't support streaming

        Example::

            async for device in MyConnectionManager.scan_stream(timeout=10.0):
                print(f"Found: {device.name}")
                if device.name == "My Target Device":
                    break  # Stop scanning early

        """
        raise NotImplementedError(f"{cls.__name__} does not support scan_stream")

    @abstractmethod
    async def get_latest_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        """Return the most recently received advertisement data.

        Args:
            refresh: If True, perform an active scan to get fresh data.
                    If False, return the last cached advertisement.

        Returns:
            Latest AdvertisementData, or None if none received yet

        """

    @classmethod
    @abstractmethod
    def convert_advertisement(cls, advertisement: object) -> AdvertisementData:
        """Convert framework-specific advertisement data to AdvertisementData.

        This method bridges the gap between BLE framework-specific advertisement
        representations (Bleak's AdvertisementData, SimpleBLE's Peripheral, etc.)
        and our unified AdvertisementData type.

        Each connection manager implementation knows how to extract manufacturer_data,
        service_data, local_name, RSSI, etc. from its framework's format.

        Args:
            advertisement: Framework-specific advertisement object
                          (e.g., bleak.backends.scanner.AdvertisementData)

        Returns:
            Unified AdvertisementData with ad_structures populated

        """


__all__ = ["ConnectionManagerProtocol"]
