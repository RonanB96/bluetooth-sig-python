"""Bleak-based connection manager moved to examples connection_managers.

This module imports Bleak at module import time so that attempting to
import it when Bleak is not available will fail fast (tests rely on
that behaviour).
"""

from __future__ import annotations

import asyncio
from typing import Callable

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTServiceCollection

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.uuid import BluetoothUUID


class BleakRetryConnectionManager(ConnectionManagerProtocol):
    """Connection manager using Bleak with retry support for robust connections."""

    def __init__(self, address: str, timeout: float = 30.0, max_attempts: int = 3) -> None:
        """Initialize the connection manager."""
        self.address = address
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.client = BleakClient(address, timeout=timeout)

    async def connect(self) -> None:
        """Connect to the device with retry logic."""
        last_exception = None
        for attempt in range(self.max_attempts):
            try:
                await self.client.connect()
                return
            except (OSError, TimeoutError) as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
                else:
                    raise last_exception from None

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        await self.client.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.client.is_connected

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read a GATT characteristic."""
        raw_data = await self.client.read_gatt_char(str(char_uuid))
        return bytes(raw_data)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes) -> None:
        """Write to a GATT characteristic."""
        await self.client.write_gatt_char(str(char_uuid), data)

    async def get_services(self) -> BleakGATTServiceCollection:
        """Get services."""
        return self.client.services

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications."""

        def adapted_callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
            callback(characteristic.uuid, bytes(data))

        await self.client.start_notify(str(char_uuid), adapted_callback)

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications."""
        await self.client.stop_notify(str(char_uuid))
