"""Connection manager protocol for BLE transport adapters.

Defines an async abstract base class that adapter implementations (Bleak,
SimplePyBLE, etc.) must inherit from so the `Device` class can operate
independently of the underlying BLE library.

Adapters must provide async implementations of all abstract methods below.
For sync-only libraries an adapter can run sync calls in a thread and
expose an async interface.
"""
# pylint: disable=duplicate-code  # Pattern repetition is expected for protocol definitions

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, ClassVar

from bluetooth_sig.types.device_types import DeviceService, ScannedDevice
from bluetooth_sig.types.uuid import BluetoothUUID


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
        """Read the RSSI (signal strength) of the connection.

        Returns:
            RSSI value in dBm (typically negative, e.g., -60)

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
    async def scan(cls, timeout: float = 5.0) -> list[ScannedDevice]:
        """Scan for nearby BLE devices.

        This is a class method that doesn't require an instance. Not all backends
        support scanning - check the `supports_scanning` class attribute.

        Args:
            timeout: Scan duration in seconds (default: 5.0)

        Returns:
            List of discovered devices

        Raises:
            NotImplementedError: If this backend doesn't support scanning

        """
        raise NotImplementedError(f"{cls.__name__} does not support scanning")


__all__ = ["ConnectionManagerProtocol"]
