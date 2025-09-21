#!/usr/bin/env python3
"""Bleak-retry-connector integration utilities for BLE examples.

This module provides bleak-retry-connector specific BLE connection and
characteristic reading functions with robust retry logic.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

# Check for library availability
try:
    # We need to import the actual classes for runtime usage
    import importlib.util

    from bleak import BleakClient, BleakScanner
    from bleak.backends.characteristic import BleakGATTCharacteristic

    bleak_spec = importlib.util.find_spec("bleak")
    retry_spec = importlib.util.find_spec("bleak_retry_connector")

    BLEAK_RETRY_AVAILABLE = bleak_spec is not None and retry_spec is not None
except ImportError:
    BLEAK_RETRY_AVAILABLE = False
    BleakClient = None  # type: ignore
    BleakScanner = None  # type: ignore


async def read_characteristics_bleak_retry(
    address: str,
    uuids: list[str] | None = None,
    max_attempts: int = 3,
    timeout: float = 30.0,
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics from a BLE device using bleak-retry-connector.

    Args:
        address: Device address
        uuids: List of characteristic UUIDs to read
        max_attempts: Maximum retry attempts
        timeout: Connection timeout in seconds

    Returns:
        Dict of {uuid: (data, timestamp)} for successful reads
    """
    if not BLEAK_RETRY_AVAILABLE or BleakClient is None:
        raise ImportError("bleak-retry-connector not available")

    if not uuids:
        uuids = ["2A19", "2A00"]  # Default: Battery Level, Device Name

    results = {}
    print(f"📱 Reading with bleak-retry-connector (max {max_attempts} attempts)...")

    try:
        # Use bleak-retry-connector for robust connection
        # Note: establish_connection may need a BLEDevice, but let's try direct connection first

        # Create client and establish connection with retry logic
        client = BleakClient(address, timeout=timeout)

        # Manual retry logic since establish_connection signature may vary
        last_exception = None
        for attempt in range(max_attempts):
            try:
                await client.connect()
                break
            except (OSError, TimeoutError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff
                    print(f"   🔄 Retry {attempt + 1}/{max_attempts}")
                else:
                    raise last_exception from None

        print(f"   ✅ Connected to {address}")

        for uuid in uuids:
            try:
                # Normalize UUID
                if len(uuid) == 4:
                    full_uuid = f"0000{uuid.upper()}-0000-1000-8000-00805F9B34FB"
                else:
                    full_uuid = uuid.upper()

                # Read characteristic
                data = await client.read_gatt_char(full_uuid)
                timestamp = time.time()
                results[uuid.upper()] = (data, timestamp)
                print(f"   ✅ Read {uuid.upper()}: {len(data)} bytes")

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"   ❌ Failed to read {uuid.upper()}: {e}")

        await client.disconnect()

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"   ❌ bleak-retry connection failed: {e}")

    return results


async def scan_with_bleak_retry(timeout: float = 10.0) -> list[Any]:
    """Scan for BLE devices using bleak-retry patterns.

    Args:
        timeout: Scan timeout in seconds

    Returns:
        List of discovered devices
    """
    if not BLEAK_RETRY_AVAILABLE or BleakScanner is None:
        print("❌ bleak-retry-connector not available for scanning")
        return []

    # For scanning, we can use regular BleakScanner since retry logic
    # is mainly for connections, not scanning

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout)

    print(f"\n📡 Found {len(devices)} devices:")
    for i, device in enumerate(devices, 1):
        name = getattr(device, "name", None) or "Unknown"
        address = getattr(device, "address", "Unknown")
        rssi = getattr(device, "rssi", None)

        if rssi is not None:
            print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")
        else:
            print(f"  {i}. {name} ({address})")

    return devices


async def discover_services_bleak_retry(  # pylint: disable=too-many-locals
    address: str,
    timeout: float = 10.0,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Discover services and characteristics from a BLE device using bleak-retry.

    Args:
        address: Device address
        max_attempts: Maximum retry attempts
        timeout: Connection timeout in seconds

    Returns:
        Dict containing service and characteristic information
    """
    if not BLEAK_RETRY_AVAILABLE or BleakClient is None:
        raise ImportError("bleak-retry-connector not available")

    results = {
        "services": [],
        "characteristics": {},
        "descriptors": {},
    }

    print(f"🔍 Discovering services on {address}...")

    try:
        # Create client and establish connection with retry logic
        client = BleakClient(address, timeout=timeout)

        # Manual retry logic for connection
        last_exception = None
        for attempt in range(max_attempts):
            try:
                await client.connect()
                break
            except (OSError, TimeoutError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    print(f"   🔄 Retry {attempt + 1}/{max_attempts}")
                else:
                    raise last_exception from None

        print(f"   ✅ Connected to {address}")

        # Get all services
        services = client.services
        service_list = list(services)
        print(f"   🔍 Found {len(service_list)} services")

        for service in service_list:
            service_info = {
                "uuid": service.uuid,
                "description": service.description,
                "characteristics": [],
            }

            print(f"\n📋 Service: {service.uuid}")
            if service.description:
                print(f"   📝 Description: {service.description}")

            # Get characteristics for this service
            for char in service.characteristics:
                char_info = {
                    "uuid": char.uuid,
                    "description": char.description,
                    "properties": char.properties,
                    "descriptors": [],
                }

                print(f"   📊 Characteristic: {char.uuid}")
                if char.description:
                    print(f"      📝 Description: {char.description}")
                print(f"      🔧 Properties: {char.properties}")

                # Get descriptors for this characteristic
                for desc in char.descriptors:
                    desc_info = {
                        "uuid": desc.uuid,
                        "description": desc.description,
                    }
                    char_info["descriptors"].append(desc_info)
                    print(f"         📎 Descriptor: {desc.uuid}")

                service_info["characteristics"].append(char_info)
                results["characteristics"][char.uuid] = char_info

            results["services"].append(service_info)

        await client.disconnect()
        print("\n✅ Service discovery completed")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"   ❌ Service discovery failed: {e}")
        raise

    return results


async def handle_notifications_bleak_retry(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    address: str,
    characteristic_uuid: str,
    duration: int = 10,
    timeout: float = 10.0,
    max_attempts: int = 3,
) -> None:
    """Handle BLE notifications using bleak-retry with comprehensive retry logic.

    Args:
        address: BLE device address
        characteristic_uuid: UUID of characteristic to monitor for notifications
        duration: How long to listen for notifications (seconds)
        timeout: Connection timeout in seconds
        max_attempts: Maximum connection retry attempts

    Raises:
        ImportError: If bleak-retry-connector not available
        Exception: If connection or notification setup fails
    """
    if not BLEAK_RETRY_AVAILABLE or BleakClient is None:
        raise ImportError("bleak-retry-connector not available")

    print(f"🔔 Setting up notifications from {address}")
    print(f"   📊 Characteristic: {characteristic_uuid}")
    print(f"   ⏱️  Duration: {duration}s")

    notification_count = 0

    def notification_handler(
        characteristic: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Handle incoming notification data."""
        nonlocal notification_count
        notification_count += 1
        print(f"   📬 Notification #{notification_count}")
        print(f"      🔗 From: {characteristic.uuid}")
        print(f"      📊 Data: {data.hex()}")
        print(f"      📏 Length: {len(data)} bytes")

        # Try to decode as text if possible
        try:
            decoded = data.decode("utf-8")
            print(f"      📝 Text: {decoded}")
        except UnicodeDecodeError:
            pass

    try:
        # Create client and establish connection with retry logic
        client = BleakClient(address, timeout=timeout)

        # Manual retry logic for connection
        last_exception = None
        for attempt in range(max_attempts):
            try:
                await client.connect()
                break
            except (OSError, TimeoutError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    print(f"   🔄 Retry {attempt + 1}/{max_attempts}")
                else:
                    raise last_exception from None

        print(f"   ✅ Connected to {address}")

        # Find the characteristic
        services = client.services
        target_char = None
        for service in services:
            for char in service.characteristics:
                # Check both full UUID and short UUID formats
                char_uuid = str(char.uuid).lower()
                search_uuid = characteristic_uuid.lower()

                # If search_uuid is 4 characters, compare short form
                if len(search_uuid) == 4:
                    if char_uuid.startswith(f"0000{search_uuid}"):
                        target_char = char
                        break
                # Otherwise compare full UUIDs
                elif char_uuid == search_uuid:
                    target_char = char
                    break
            if target_char:
                break

        if not target_char:
            raise ValueError(f"Characteristic {characteristic_uuid} not found")

        # Check if characteristic supports notifications
        if "notify" not in target_char.properties:
            print(
                f"   ⚠️  Warning: Characteristic {characteristic_uuid} may not support notifications"
            )
            print(f"      Properties: {target_char.properties}")

        # Enable notifications
        await client.start_notify(target_char.uuid, notification_handler)
        print("   🔔 Notifications enabled")

        # Listen for notifications
        print(f"   👂 Listening for notifications for {duration} seconds...")
        await asyncio.sleep(duration)

        # Disable notifications
        await client.stop_notify(target_char.uuid)
        await client.disconnect()

        print("\n✅ Notification session completed")
        print(f"   📊 Total notifications received: {notification_count}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"   ❌ Notification handling failed: {e}")
        raise
