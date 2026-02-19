"""High-level helper wrappers for Bleak-backed connection manager.

These helpers provide the example-level conveniences previously offered
by the removed ``examples.utils.bleak_retry_integration`` module but
delegate actual device interaction to the ``BleakRetryClientManager``
implementation. Placing these helpers alongside the concrete manager
keeps bleak imports in one place and satisfies tests that expect a
fast-failure when bleak is not installed.
"""

from __future__ import annotations

import asyncio
import importlib
from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from bluetooth_sig.types.io import RawCharacteristicBatch, RawCharacteristicRead
from examples.utils.connection_helpers import read_characteristics_with_manager
from examples.utils.device_scanning import safe_get_device_info
from examples.utils.models import DeviceInfo, ReadResult


class _DescriptorLike(Protocol):
    uuid: object
    value: bytes | bytearray | None


class _CharacteristicLike(Protocol):
    uuid: object
    properties: Sequence[str] | None
    descriptors: Iterable[_DescriptorLike] | None
    value: bytes | bytearray | None


class _ServiceLike(Protocol):
    characteristics: Iterable[_CharacteristicLike] | None


def bleak_services_to_batch(
    services: Iterable[_ServiceLike] | None,
    values_by_uuid: Mapping[str, bytes] | None = None,
) -> RawCharacteristicBatch:
    """Build a RawCharacteristicBatch from Bleak service metadata.

    This function avoids a hard dependency on Bleak by using duck typing. It
    expects an iterable of service-like objects, each having a `.characteristics`
    iterable with items that expose a `.uuid` attribute and (optionally)
    `.properties` and `.descriptors`.

    The function does not perform I/O. Provide `values_by_uuid` if you have
    separate read results keyed by characteristic UUID (short or full form).
    Descriptors are included when characteristic descriptors expose both
    `.uuid` and `.value` bytes.
    """
    items: list[RawCharacteristicRead] = []

    for service in services or []:
        chars = getattr(service, "characteristics", [])
        for char in chars:
            uuid = str(char.uuid)
            raw: bytes | None = None

            # Prefer explicit values map if provided
            if values_by_uuid is not None:
                raw = values_by_uuid.get(uuid) or values_by_uuid.get(uuid.upper()) or values_by_uuid.get(uuid.lower())

            # Fallback to attribute commonly present on some wrappers
            if raw is None:
                raw = getattr(char, "value", None)

            if raw is None:
                continue  # skip characteristics without a value

            props = list(getattr(char, "properties", []) or [])

            # Collect descriptor raw values when available
            desc_bytes: dict[str, bytes] = {}
            for desc in getattr(char, "descriptors", []) or []:
                d_uuid = str(getattr(desc, "uuid", ""))
                d_val = getattr(desc, "value", None)
                if d_uuid and isinstance(d_val, (bytes, bytearray)):
                    desc_bytes[d_uuid] = bytes(d_val)

            items.append(
                RawCharacteristicRead(uuid=uuid, raw_data=bytes(raw), descriptors=desc_bytes, properties=props)
            )

    return RawCharacteristicBatch(items=items)


async def scan_with_bleak_retry(timeout: float = 10.0) -> list[DeviceInfo]:
    """Scan for BLE devices using Bleak's scanner and normalise results.

    Returns a list of :class:`DeviceInfo` instances for example consumers.
    """
    print(f"Scanning for BLE devices ({timeout}s)...")
    # Import BleakScanner at runtime to avoid import-time dependency.
    bleak = importlib.import_module("bleak")
    BleakScanner = bleak.BleakScanner
    devices = await BleakScanner.discover(timeout=timeout)

    print(f"\nFound {len(devices)} devices:")
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
    """Read characteristics from a device using the BleakRetryClientManager.

    This is a thin convenience wrapper that constructs a manager and
    delegates to the canonical connection helper. It preserves the
    example-facing ``ReadResult`` mapping used elsewhere in the
    examples package.
    """
    # Dynamically import the concrete manager so that static analysis
    # and environments without Bleak do not attempt to import BleakRetry
    # at module import time.
    bleak_mod = importlib.import_module("examples.connection_managers.bleak_retry")
    BleakRetryClientManager = bleak_mod.BleakRetryClientManager
    manager = BleakRetryClientManager(address, timeout=timeout, max_attempts=max_attempts)
    return await read_characteristics_with_manager(manager, uuids)


async def handle_notifications_bleak_retry(
    address: str, characteristic_uuid: str, duration: int = 10, timeout: float = 10.0, max_attempts: int = 3
) -> None:
    """Register and handle notifications from a characteristic for a period.

    Creates a manager, connects, registers a simple print callback and
    waits for the requested duration before cleaning up.
    """
    bleak_mod = importlib.import_module("examples.connection_managers.bleak_retry")
    BleakRetryClientManager = bleak_mod.BleakRetryClientManager
    manager = BleakRetryClientManager(address, timeout=timeout, max_attempts=max_attempts)
    await manager.connect()

    def _cb(char_uuid: str, data: bytes) -> None:
        print(f"Notification from {char_uuid}: {data.hex()}")

    try:
        await manager.start_notify(characteristic_uuid, _cb)
        print("   Notifications enabled")
        await asyncio.sleep(duration)
        await manager.stop_notify(characteristic_uuid)
        print("\nNotification session completed")
    finally:
        await manager.disconnect()
