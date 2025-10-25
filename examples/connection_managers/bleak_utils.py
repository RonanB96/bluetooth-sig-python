"""High-level helper wrappers for Bleak-backed connection manager.

These helpers provide the example-level conveniences previously offered
by the removed ``examples.utils.bleak_retry_integration`` module but
delegate actual device interaction to the ``BleakRetryConnectionManager``
implementation. Placing these helpers alongside the concrete manager
keeps bleak imports in one place and satisfies tests that expect a
fast-failure when bleak is not installed.
"""

from __future__ import annotations

import asyncio
import importlib

from examples.utils.connection_helpers import read_characteristics_with_manager
from examples.utils.device_scanning import safe_get_device_info
from examples.utils.models import DeviceInfo, ReadResult


async def scan_with_bleak_retry(timeout: float = 10.0) -> list[DeviceInfo]:
    """Scan for BLE devices using Bleak's scanner and normalise results.

    Returns a list of :class:`DeviceInfo` instances for example consumers.
    """
    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    # Import BleakScanner at runtime to avoid import-time dependency.
    bleak = importlib.import_module("bleak")
    BleakScanner = bleak.BleakScanner
    devices = await BleakScanner.discover(timeout=timeout)

    print(f"\n📡 Found {len(devices)} devices:")
    normalized: list[DeviceInfo] = []
    for i, device in enumerate(devices, 1):
        name, address, rssi = safe_get_device_info(device)
        rssi_int = int(rssi) if rssi is not None else None
        if rssi_int is not None:
            print(f"  {i}. {name} ({address}) - RSSI: {rssi_int}dBm")
        else:
            print(f"  {i}. {name} ({address})")
        normalized.append(DeviceInfo(name=name, address=address, rssi=rssi_int, raw=device))

    return normalized


async def read_characteristics_bleak_retry(
    address: str, uuids: list[str] | None = None, max_attempts: int = 3, timeout: float = 30.0
) -> dict[str, ReadResult]:
    """Read characteristics from a device using the BleakRetryConnectionManager.

    This is a thin convenience wrapper that constructs a manager and
    delegates to the canonical connection helper. It preserves the
    example-facing ``ReadResult`` mapping used elsewhere in the
    examples package.
    """
    # Dynamically import the concrete manager so that static analysis
    # and environments without Bleak do not attempt to import BleakRetry
    # at module import time.
    bleak_mod = importlib.import_module("examples.connection_managers.bleak_retry")
    BleakRetryConnectionManager = bleak_mod.BleakRetryConnectionManager
    manager = BleakRetryConnectionManager(address, timeout=timeout, max_attempts=max_attempts)
    return await read_characteristics_with_manager(manager, uuids)


async def handle_notifications_bleak_retry(
    address: str, characteristic_uuid: str, duration: int = 10, timeout: float = 10.0, max_attempts: int = 3
) -> None:
    """Register and handle notifications from a characteristic for a period.

    Creates a manager, connects, registers a simple print callback and
    waits for the requested duration before cleaning up.
    """
    bleak_mod = importlib.import_module("examples.connection_managers.bleak_retry")
    BleakRetryConnectionManager = bleak_mod.BleakRetryConnectionManager
    manager = BleakRetryConnectionManager(address, timeout=timeout, max_attempts=max_attempts)
    await manager.connect()

    def _cb(char_uuid: str, data: bytes) -> None:
        print(f"Notification from {char_uuid}: {data.hex()}")

    try:
        await manager.start_notify(characteristic_uuid, _cb)
        print("   🔔 Notifications enabled")
        await asyncio.sleep(duration)
        await manager.stop_notify(characteristic_uuid)
        print("\n✅ Notification session completed")
    finally:
        await manager.disconnect()
