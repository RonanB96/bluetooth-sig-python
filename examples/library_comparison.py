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


# Import shared BLE utilities
from ble_utils import (
    AVAILABLE_LIBRARIES,
    demo_library_comparison,
    get_default_characteristic_uuids,
    parse_and_display_results,
    read_characteristics_bleak,
    read_characteristics_bleak_retry,
    scan_with_bleak,
    show_library_availability,
)


async def compare_libraries(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    address: str, target_uuids: list[str] = None, use_comprehensive: bool = True
):
    """Compare different BLE libraries with comprehensive device analysis or specific UUIDs.

    Args:
        address: BLE device address
        target_uuids: Specific UUIDs to test, or None for comprehensive analysis
        use_comprehensive: If True, use comprehensive device analysis instead of predefined UUIDs
    """

    if use_comprehensive and target_uuids is None:
        print(f"\n🔍 Comprehensive BLE Library Comparison for device: {address}")
        print("=" * 60)
        print("Discovering and testing ALL device characteristics!")

        # Use the shared comprehensive comparison function
        results = await demo_library_comparison(address)

        print("\n📊 Comprehensive Analysis Summary")
        print("=" * 40)

        for library, result in results.items():
            if "stats" in result:
                stats = result["stats"]
                print(f"\n{library.upper()} Library:")
                print(f"  🔗 Connection time: {stats['connection_time']:.2f}s")
                print(f"  🔧 Services discovered: {stats['services_discovered']}")
                print(f"  📋 Characteristics found: {stats['characteristics_found']}")
                print(f"  📖 Characteristics read: {stats['characteristics_read']}")
                print(f"  🏗️  Characteristics parsed: {stats['characteristics_parsed']}")
                print(
                    f"  ✅ Characteristics validated: {stats['characteristics_validated']}"
                )

        print("\n💡 This approach discovers actual device capabilities")
        print("   instead of testing predefined characteristics.")

        return results

    # Legacy mode: test specific UUIDs
    if target_uuids is None:
        target_uuids = get_default_characteristic_uuids()
        print("⚠️  Using legacy predefined characteristic list:")
        print(f"   {', '.join(target_uuids)}")
        print("   💡 Use --comprehensive for real device discovery")

    print(f"\n🔍 Legacy BLE Library Comparison for device: {address}")
    print("=" * 55)
    print("Testing predefined characteristics - limited scope!")

    # Dictionary to store results from each library
    library_results = {}
    library_timings = {}
    connection_success = {}

    # Test with Bleak
    if "bleak" in AVAILABLE_LIBRARIES:
        print("\n📱 Testing Bleak library...")
        start_time = time.time()
        try:
            bleak_data = await read_characteristics_bleak(address, target_uuids)
            library_timings["bleak"] = time.time() - start_time
            library_results["bleak"] = await parse_and_display_results(
                bleak_data, "Bleak"
            )
            connection_success["bleak"] = len(bleak_data) > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            library_timings["bleak"] = time.time() - start_time
            library_results["bleak"] = {}
            connection_success["bleak"] = False
            print(f"   ❌ Bleak failed: {e}")

    # Test with Bleak-retry-connector
    if "bleak-retry" in AVAILABLE_LIBRARIES:
        print("\n🔄 Testing Bleak-retry-connector...")
        start_time = time.time()
        try:
            retry_data = await read_characteristics_bleak_retry(address, target_uuids)
            library_timings["bleak-retry"] = time.time() - start_time
            library_results["bleak-retry"] = await parse_and_display_results(
                retry_data, "Bleak-Retry"
            )
            connection_success["bleak-retry"] = len(retry_data) > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            library_timings["bleak-retry"] = time.time() - start_time
            library_results["bleak-retry"] = {}
            connection_success["bleak-retry"] = False
            print(f"   ❌ Bleak-retry failed: {e}")

    # Summary of library performance
    print("\n📊 Library Performance Summary")
    print("=" * 40)

    successful_libraries = [
        lib for lib, success in connection_success.items() if success
    ]

    if not successful_libraries:
        print("❌ No libraries successfully connected to the device!")
        print("Possible issues:")
        print("  • Device not in range or not advertising")
        print("  • Incorrect address")
        print("  • Device already connected elsewhere")
        print("  • Bluetooth permissions/pairing issues")
        return

    print(
        f"✅ {len(successful_libraries)}/{len(connection_success)} libraries connected successfully"
    )

    for lib_name, success in connection_success.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        timing = library_timings.get(lib_name, 0)
        reads = len(library_results.get(lib_name, {}))
        print(f"   {lib_name}: {status} - {timing:.2f}s, {reads} characteristics read")

    # Compare parsing results (only for successful connections)
    if len(successful_libraries) > 1:
        print("\n🔍 SIG Parsing Consistency Check")
        print("=" * 40)

        for uuid_short in target_uuids:
            print(f"\n📊 Characteristic {uuid_short}:")

            values = []
            for lib_name in successful_libraries:
                if uuid_short in library_results[lib_name]:
                    value = library_results[lib_name][uuid_short]["value"]
                    values.append(value)
                    print(f"   {lib_name}: {value}")

        if len(values) > 1 and len(set(str(v) for v in values)) == 1:
            print("   ✅ bluetooth_sig parsing identical across all libraries!")
        elif len(values) > 1:
            print("   ⚠️  Different parsed values - unexpected!")
        else:
            print("   ℹ️  Only one library read this characteristic")

    elif len(successful_libraries) == 1:
        print(f"\n📊 Only {successful_libraries[0]} connected successfully")
        print("Need multiple working libraries to compare parsing consistency")

    print("\n🎯 Key Takeaway:")
    print("  • Library connection success rates vary (real-world difference)")
    print("  • Performance varies between libraries (real-world difference)")
    print("  • bluetooth_sig parsing is identical when connections succeed")
    print("  • Choose BLE library based on reliability/performance for your use case")

    return library_results


async def main():
    """Main function for BLE library comparison."""
    parser = argparse.ArgumentParser(
        description="BLE library comparison with bluetooth_sig"
    )
    parser.add_argument("--address", "-a", help="BLE device address to test")
    parser.add_argument(
        "--scan", "-s", action="store_true", help="Scan for devices first"
    )
    parser.add_argument(
        "--compare-all",
        "-c",
        action="store_true",
        help="Compare all available libraries",
    )
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific UUIDs to test")
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        default=True,
        help="Use comprehensive device analysis",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy mode with predefined characteristics",
    )

    args = parser.parse_args()

    has_libraries = show_library_availability()
    if not has_libraries:
        print("No BLE libraries available. Install bleak or bleak-retry-connector.")
        return

    if not args.address:
        if args.scan:
            devices = await scan_with_bleak()
            if devices:
                print("Found devices:")
                for device in devices:
                    name = device.name or "Unknown"
                    print(f"  {name} ({device.address})")
            else:
                print("No devices found.")
        else:
            print("Usage: python library_comparison.py --address <BLE_ADDRESS>")
        return

    use_comprehensive = not args.legacy
    if args.uuids:
        use_comprehensive = False

    try:
        await compare_libraries(args.address, args.uuids, use_comprehensive)
    except KeyboardInterrupt:
        print("Comparison interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
