#!/usr/bin/env python3
"""Connection helpers shared by examples.

This module provides small, well-typed helpers that operate on the
``ConnectionManagerProtocol`` abstraction used throughout the examples.

Historically these helpers lived in a deprecated ``shared_utils.py``
module. They have been moved here so the examples can import them from
``examples.utils`` without pulling in deprecated code.
"""

from __future__ import annotations

import time

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.uuid import BluetoothUUID
from examples.utils.models import ReadResult


async def read_characteristics_with_manager(
    connection_manager: ConnectionManagerProtocol,
    target_uuids: list[str] | None = None,
    timeout: float = 10.0,
) -> dict[str, ReadResult]:
    """Read characteristics from a BLE device using a connection manager.

    This is the canonical implementation previously included in the
    examples' deprecated utilities. It discovers readable characteristics
    when none are provided and returns raw bytes together with the read
    duration for each characteristic.

    Args:
        connection_manager: The connection manager implementing the
            :class:`ConnectionManagerProtocol` interface.
        target_uuids: Optional list of UUIDs to read. If ``None`` the
            function will perform a service discovery and attempt to read
            all readable characteristics it finds.
        timeout: Unused in the current implementation but kept for API
            compatibility with older example callers.

    Returns:
        Mapping from short-UUID string (e.g. "2A19") to ``(raw_bytes,
        read_time_seconds)``.
    """
    del timeout

    results: dict[str, ReadResult] = {}
    print("Reading characteristics with connection manager...")

    try:
        await connection_manager.connect()
        print("✅ Connected, reading characteristics...")

        # If no UUIDs were specified, discover services and pick readable
        # characteristics. The exact shape of ``get_services()`` can vary
        # across adapters, so be defensive when inspecting attributes.
        if target_uuids is None:
            services = await connection_manager.get_services()
            discovered: list[str] = []
            for service in services:
                if hasattr(service, "characteristics"):
                    for char in service.characteristics:
                        try:
                            if hasattr(char, "properties") and "read" in char.properties:
                                discovered.append(str(char.uuid))
                        except Exception:
                            # Be resilient to unusual service/char shapes
                            continue
            target_uuids = discovered
            print(f"Found {len(target_uuids)} readable characteristics")
        else:
            # Expand short UUIDs into the full 128-bit form for adapters
            expanded: list[str] = []
            for uuid in target_uuids:
                if len(uuid) == 4:
                    expanded.append(f"0000{uuid}-0000-1000-8000-00805F9B34FB")
                else:
                    expanded.append(uuid)
            target_uuids = expanded

        # Read each requested characteristic and record the elapsed time
        for uuid in target_uuids:
            try:
                read_start = time.time()
                raw_data = await connection_manager.read_gatt_char(BluetoothUUID(uuid))
                read_time = time.time() - read_start

                uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                results[uuid_key] = ReadResult(raw_data=bytes(raw_data), read_time=read_time)
                print(f"  {uuid_key}: {len(raw_data)} bytes")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                results[uuid_key] = ReadResult(raw_data=b"", read_time=0.0, error=str(exc))
                print(f"  {uuid_key}: {exc}")

        await connection_manager.disconnect()
        print("✅ Disconnected")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Connection failed: {exc}")

    return results
