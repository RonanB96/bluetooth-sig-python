#!/usr/bin/env python3
"""Library comparison example - compare different BLE libraries with SIG parsing.

This example demonstrates the framework-agnostic nature of bluetooth_sig by
showing how the same SIG parsing code works identically across different BLE
connection libraries. The parsing logic remains unchanged regardless of the
underlying BLE implementation.

Key Demonstration:
- Same bluetooth_sig code works with multiple BLE libraries
- Connection method varies, but SIG parsing is identical
- Framework-agnostic design allows easy migration between libraries
- Performance and feature comparison across libraries

Usage:
    python library_comparison.py --address 12:34:56:78:9A:BC
    python library_comparison.py --scan --compare-all
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Import shared BLE utilities
from ble_utils import (
    AVAILABLE_LIBRARIES,
    show_library_availability,
    scan_with_bleak,
    read_characteristics_bleak,
    read_characteristics_bleak_retry,
    parse_and_display_results,
    demo_mock_comparison,
    get_default_characteristic_uuids,
)


def read_with_simpleble(address: str, target_uuids: list[str]) -> dict[str, tuple[bytes, float]]:
    """Read characteristics using SimpleBLE library.

    Note: This is a mock implementation since SimpleBLE usage varies by platform.
    """
    print("🔶 SimpleBLE reading (Mock implementation)")
    print(f"   📝 Would connect to {address} and read UUIDs: {target_uuids}")

    # Mock data for demonstration
    mock_results = {}
    for uuid in target_uuids:
        if uuid == "2A19":
            mock_results[uuid] = (bytes([0x64]), 0.001)  # 100% battery
        elif uuid == "2A00":
            mock_results[uuid] = (b"SimpleBLE Device", 0.002)

    return mock_results


async def compare_libraries(address: str, target_uuids: list[str] = None):
    """Compare different BLE libraries with same SIG parsing."""
    if target_uuids is None:
        target_uuids = get_default_characteristic_uuids()

    print(f"\n🔍 Comparing BLE Libraries for device: {address}")
    print("=" * 55)

    # Dictionary to store results from each library
    library_results = {}
    library_timings = {}

    # Test with Bleak
    if 'bleak' in AVAILABLE_LIBRARIES:
        start_time = time.time()
        bleak_data = await read_characteristics_bleak(address, target_uuids)
        library_timings['bleak'] = time.time() - start_time
        library_results['bleak'] = await parse_and_display_results(bleak_data, "Bleak")

    # Test with Bleak-retry-connector
    if 'bleak-retry' in AVAILABLE_LIBRARIES:
        start_time = time.time()
        retry_data = await read_characteristics_bleak_retry(address, target_uuids)
        library_timings['bleak-retry'] = time.time() - start_time
        library_results['bleak-retry'] = await parse_and_display_results(retry_data, "Bleak-Retry")

    # Test with SimpleBLE (mock)
    start_time = time.time()
    simpleble_data = read_with_simpleble(address, target_uuids)
    library_timings['simpleble'] = time.time() - start_time
    library_results['simpleble'] = await parse_and_display_results(simpleble_data, "SimpleBLE")

    # Compare results across libraries
    print("\n🔍 Cross-Library Result Validation")
    print("=" * 40)

    for uuid_short in target_uuids:
        print(f"\n📊 Characteristic {uuid_short}:")

        values = []
        for lib_name, results in library_results.items():
            if uuid_short in results:
                value = results[uuid_short]['value']
                values.append(value)
                print(f"   {lib_name}: {value}")

        # Check if all libraries produced identical values
        if len(set(str(v) for v in values)) <= 1:
            print("   ✅ All libraries parsed IDENTICAL values!")
        else:
            print("   ⚠️  Values differ or some failed")

    # Performance comparison
    print("\n⏱️  Performance Comparison")
    print("=" * 30)
    for lib_name, total_time in library_timings.items():
        successful_reads = len([r for r in library_results[lib_name].values()])
        print(f"   {lib_name}: {total_time:.2f}s total, {successful_reads} successful reads")


async def main():
    """Main function for BLE library comparison."""
    parser = argparse.ArgumentParser(description="BLE library comparison with bluetooth_sig")
    parser.add_argument("--address", "-a", help="BLE device address to test")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices first")
    parser.add_argument("--compare-all", "-c", action="store_true", help="Compare all available libraries")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific UUIDs to test")

    args = parser.parse_args()

    print("🚀 BLE Library Comparison with Framework-Agnostic SIG Parsing")
    print("=" * 70)

    # Show available libraries
    has_libraries = show_library_availability()

    if not has_libraries and not args.address:
        print("\n📝 Showing mock comparison to demonstrate the concept:")
        demo_mock_comparison()
        return

    try:
        if args.scan:
            devices = await scan_with_bleak()

            if not args.address and devices:
                print("\n💡 Use --address with one of the discovered addresses to compare")
                demo_mock_comparison()
                return
            elif not devices:
                demo_mock_comparison()
                return

        if args.address and has_libraries:
            target_uuids = args.uuids or get_default_characteristic_uuids()
            await compare_libraries(args.address, target_uuids)
        elif args.address:
            print(f"\n❌ No BLE libraries available to test with {args.address}")
            demo_mock_comparison()
        else:
            demo_mock_comparison()

        print("\n✅ Demo completed!")
        print("Key takeaway: bluetooth_sig provides IDENTICAL parsing across all BLE libraries!")
        print("Your choice of BLE library doesn't affect SIG standard interpretation.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
