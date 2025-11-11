"""BluePy-based connection manager for BLE devices.

This module provides a connection manager implementation using BluePy,
following the same pattern as Bleak and SimplePyBLE managers.
"""

from __future__ import annotations

from typing import Any, Callable

from bluepy.btle import ADDR_TYPE_RANDOM, UUID, Peripheral  # type: ignore[import-not-found]

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.uuid import BluetoothUUID


class BluePyConnectionManager(ConnectionManagerProtocol):
    """Connection manager using BluePy for BLE communication.

    Implements ConnectionManagerProtocol to integrate BluePy with
    the bluetooth-sig-python Device class.
    """

    def __init__(self, address: str, addr_type: str = ADDR_TYPE_RANDOM) -> None:
        """Initialize the connection manager.

        Args:
            address: BLE MAC address
            addr_type: Address type (ADDR_TYPE_RANDOM or ADDR_TYPE_PUBLIC)
        """
        self.address = address
        self.addr_type = addr_type
        self.periph: Peripheral | None = None  # type: ignore[no-any-unimported]

    async def connect(self) -> None:
        """Connect to device."""
        self.periph = Peripheral(self.address, addrType=self.addr_type)

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self.periph:
            self.periph.disconnect()
            self.periph = None

    @property
    def is_connected(self) -> bool:
        """Check if connected.

        Returns:
            True if connected
        """
        return self.periph is not None

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read GATT characteristic.

        Args:
            char_uuid: Characteristic UUID

        Returns:
            Raw characteristic bytes

        Raises:
            RuntimeError: If not connected or read fails
        """
        if not self.periph:
            raise RuntimeError("Not connected")

        try:
            characteristics = self.periph.getCharacteristics(uuid=UUID(str(char_uuid)))
            if not characteristics:
                raise RuntimeError(f"Characteristic {char_uuid} not found")

            char = characteristics[0]
            return bytes(char.read())  # type: ignore[no-any-return,attr-defined]
        except Exception as e:
            raise RuntimeError(f"Failed to read characteristic {char_uuid}: {e}") from e

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes) -> None:
        """Write GATT characteristic.

        Args:
            char_uuid: Characteristic UUID
            data: Data to write

        Raises:
            RuntimeError: If not connected or write fails
        """
        if not self.periph:
            raise RuntimeError("Not connected")

        try:
            characteristics = self.periph.getCharacteristics(uuid=UUID(str(char_uuid)))
            if not characteristics:
                raise RuntimeError(f"Characteristic {char_uuid} not found")

            char = characteristics[0]
            char.write(data)  # type: ignore[attr-defined]
        except Exception as e:
            raise RuntimeError(f"Failed to write characteristic {char_uuid}: {e}") from e

    async def get_services(self) -> Any:  # noqa: ANN401
        """Get services from device.

        Returns:
            Services structure from BluePy
        """
        if not self.periph:
            raise RuntimeError("Not connected")
        return self.periph.getServices()  # type: ignore[no-any-return,union-attr]

    async def start_notify(
        self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]
    ) -> None:
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
