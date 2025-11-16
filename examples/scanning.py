#!/usr/bin/env python3
"""Example: Scanning for BLE devices using Device.scan().

This example shows how to use the Device.scan() method to discover
nearby BLE devices without bypassing the abstraction layer.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from bluetooth_sig.device import Device


async def main() -> None:
    """Demonstrate BLE device scanning."""
    print("=" * 70)
    print("BLE Device Scanning Example")
    print("=" * 70)

    # Import the connection manager you want to use
    try:
        from connection_managers.bleak_retry import BleakRetryConnectionManager  # type: ignore[import-not-found]
    except ImportError:
        print("❌ Bleak not installed. Install with: pip install bleak")
        return

    # Check if this backend supports scanning
    if not BleakRetryConnectionManager.supports_scanning:
        print("❌ This connection manager doesn't support scanning")
        return

    print("\n📡 Scanning for BLE devices (10 seconds)...\n")

    # Scan for devices using Device.scan()
    devices = await Device.scan(BleakRetryConnectionManager, timeout=10.0)

    if not devices:
        print("No devices found")
        return

    print(f"Found {len(devices)} device(s):\n")

    # Display all discovered devices
    for i, device in enumerate(devices, 1):
        name = device.name or "Unknown"
        print(f"{i}. {name}")
        print(f"   Address: {device.address}")

        # Access data from advertisement_data if available
        if device.advertisement_data:
            adv = device.advertisement_data
            if adv.rssi is not None:
                print(f"   RSSI: {adv.rssi} dBm")
            if adv.ad_structures.core.service_uuids:
                print(f"   Services: {len(adv.ad_structures.core.service_uuids)} advertised")
            if adv.ad_structures.core.manufacturer_data:
                print(f"   Manufacturer data: {len(adv.ad_structures.core.manufacturer_data)} entries")
            if adv.ad_structures.core.local_name:
                print(f"   Local name: {adv.ad_structures.core.local_name}")
        print()

    # Example: Connect to the first device with a name
    selected = next((d for d in devices if d.name), devices[0])
    print(f"✓ Selected: {selected.name or 'Unknown'} ({selected.address})")

    print("\n💡 You can now create a Device instance:")
    print("   translator = BluetoothSIGTranslator()")
    print(f"   device = Device('{selected.address}', translator)")
    print(f"   manager = BleakRetryConnectionManager('{selected.address}')")
    print("   device.attach_connection_manager(manager)")
    print("   await device.connect()")


if __name__ == "__main__":
    asyncio.run(main())
