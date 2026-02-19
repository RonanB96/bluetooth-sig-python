"""Example: Async BLE integration with bluetooth-sig library.

This example demonstrates how to use the BluetoothSIGTranslator
with the Bleak BLE library for non-blocking characteristic parsing.

Requirements:
    pip install bluetooth-sig bleak

Usage:
    python examples/async_ble_integration.py
"""

import asyncio
from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

# Optional: Import bleak if available
try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakError

    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    print("Warning: Bleak not installed. Install with: pip install bleak")
    # Define a fallback if bleak not available for type hints
    BleakError = Exception  # type: ignore[misc,assignment]


async def scan_and_connect() -> None:
    """Scan for BLE devices and connect to the first one found."""
    if not BLEAK_AVAILABLE:
        print("Bleak is required for this example.")
        return

    translator = BluetoothSIGTranslator()

    # Scan for devices
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=5.0)

    if not devices:
        print("No devices found")
        return

    # Display found devices
    print(f"\nFound {len(devices)} device(s):")
    for i, device in enumerate(devices):
        print(f"  {i + 1}. {device.name or 'Unknown'} ({device.address})")

    # Connect to first device
    device = devices[0]
    print(f"\nConnecting to {device.name} ({device.address})...")

    try:
        async with BleakClient(device.address) as client:
            print("Connected!")

            # Discover services
            services = client.services
            service_list = list(services)
            print(f"\nDiscovered {len(service_list)} service(s)")

            # Read and parse characteristics
            for service in service_list:
                print(f"\nService: {service.uuid}")

                for char in service.characteristics:
                    if "read" in char.properties:
                        try:
                            # Read characteristic
                            data = await client.read_gatt_char(char.uuid)

                            # Parse with async API - returns value directly
                            try:
                                result = await translator.parse_characteristic_async(str(char.uuid), bytes(data))
                                print(f"  {char.uuid}: {result}")
                            except CharacteristicParseError:
                                print(f"  {char.uuid}: <unknown>")

                        except (BleakError, asyncio.TimeoutError, OSError) as e:
                            print(f"  Error reading {char.uuid}: {e}")

    except (BleakError, asyncio.TimeoutError, OSError) as e:
        print(f"Connection error: {e}")


async def batch_parsing_example() -> None:
    """Demonstrate batch parsing of multiple characteristics."""
    translator = BluetoothSIGTranslator()

    print("\n" + "=" * 50)
    print("Batch Parsing Example")
    print("=" * 50)

    # Simulate reading multiple characteristics
    char_data = {
        "2A19": bytes([85]),  # Battery Level: 85%
        "2A6E": bytes([0x90, 0x01]),  # Temperature: 4.0°C
        "2A6F": bytes([0x64, 0x09]),  # Humidity: 24.2%
    }

    # Parse all at once
    print("\nParsing multiple characteristics asynchronously...")
    results = await translator.parse_characteristics_async(char_data)

    print(f"\nParsed {len(results)} characteristic(s):")
    for uuid, result in results.items():
        print(f"  {uuid}: {result}")


async def concurrent_parsing_example() -> None:
    """Demonstrate concurrent parsing of multiple devices."""
    translator = BluetoothSIGTranslator()

    print("\n" + "=" * 50)
    print("Concurrent Parsing Example")
    print("=" * 50)

    async def parse_battery(device_id: int, level: int) -> tuple[int, Any]:
        """Simulate parsing battery from a device."""
        await asyncio.sleep(0.1)  # Simulate network delay
        data = bytes([level])
        result = await translator.parse_characteristic_async("2A19", data)
        return device_id, result

    # Parse battery levels from multiple devices concurrently
    print("\nParsing battery levels from 5 simulated devices...")
    tasks = [parse_battery(i, 50 + i * 10) for i in range(5)]

    results = await asyncio.gather(*tasks)

    print("\nResults:")
    for device_id, result in results:
        print(f"  Device {device_id}: {result}%")


async def context_manager_example() -> None:
    """Demonstrate using AsyncParsingSession context manager."""
    from bluetooth_sig import AsyncParsingSession

    print("\n" + "=" * 50)
    print("Context Manager Example")
    print("=" * 50)

    print("\nUsing AsyncParsingSession to maintain context...")

    translator = BluetoothSIGTranslator()
    async with AsyncParsingSession(translator) as session:
        # Parse multiple characteristics with shared context
        result1 = await session.parse("2A19", bytes([75]))
        print(f"  Battery Level: {result1}%")

        result2 = await session.parse("2A6E", bytes([0x90, 0x01]))
        print(f"  Temperature: {result2}°C")

        print(f"\nTotal characteristics parsed in session: {len(session.results)}")


async def main() -> None:
    """Run all examples."""
    print("=" * 50)
    print("Async BLE Integration Examples")
    print("=" * 50)

    # Run batch parsing example (doesn't require BLE hardware)
    await batch_parsing_example()

    # Run concurrent parsing example
    await concurrent_parsing_example()

    # Run context manager example
    await context_manager_example()

    # Try to scan and connect if Bleak is available
    if BLEAK_AVAILABLE:
        print("\n" + "=" * 50)
        print("Live BLE Scanning (requires BLE hardware)")
        print("=" * 50)
        try:
            await scan_and_connect()
        except (BleakError, asyncio.TimeoutError, OSError) as e:
            print(f"BLE scanning not available: {e}")
            print("This is expected in environments without Bluetooth hardware.")
    else:
        print("\n" + "=" * 50)
        print("Note: Install 'bleak' to run live BLE scanning example")
        print("  pip install bleak")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
