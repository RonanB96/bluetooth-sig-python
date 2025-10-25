#!/usr/bin/env python3
"""Generic notification handling utilities for examples.

This module provides notification handling that works with any
connection manager that implements the ConnectionManagerProtocol.
"""

from __future__ import annotations

import asyncio

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.uuid import BluetoothUUID


async def handle_notifications_generic(
    connection_manager: ConnectionManagerProtocol,
    characteristic_uuid: str,
    duration: int = 10,
) -> None:
    """Register and handle notifications from a characteristic for a period.

    Works with any connection manager that implements ConnectionManagerProtocol.

    Args:
        connection_manager: The connection manager to use
        characteristic_uuid: UUID of the characteristic to monitor
        duration: How long to listen for notifications in seconds
    """

    def _cb(char_uuid: str, data: bytes) -> None:
        print(f"Notification from {char_uuid}: {data.hex()}")

    # Convert string UUID to BluetoothUUID
    uuid_obj = BluetoothUUID(characteristic_uuid)

    try:
        await connection_manager.start_notify(uuid_obj, _cb)
        print("   🔔 Notifications enabled")
        await asyncio.sleep(duration)
        await connection_manager.stop_notify(uuid_obj)
        print("\n✅ Notification session completed")
    finally:
        await connection_manager.disconnect()
