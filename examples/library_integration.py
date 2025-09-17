#!/usr/bin/env python3
"""Library integration examples for different BLE libraries."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared_utils import (
    create_device,
    parse_results,
    read_characteristics,
    setup_library_check,
)


async def demo_bleak_integration(address: str):
    """Demonstrate integration with Bleak library."""
    print(f"Bleak Integration Example with {address}")

    raw_results = await read_characteristics(address)
    if raw_results:
        parsed_results = parse_results(raw_results)
        print(f"Successfully parsed {len(parsed_results)} characteristics")
        for uuid, result in parsed_results.items():
            if result is not None:
                print(f"  {uuid}: {result}")


async def demo_device_integration(address: str):
    """Demonstrate Device class integration pattern."""
    print(f"Device Class Integration Example with {address}")

    device = create_device(address)
    print(f"Created device: {device}")

    # In a real application, you would:
    # 1. Attach a connection manager
    # 2. Use the new Device methods
    print("Available Device methods:")
    print("- discover_services()")
    print("- read_multiple()")
    print("- write_multiple()")
    print("- is_connected property")


async def main():
    """Main function for library integration examples."""
    parser = argparse.ArgumentParser(description="BLE library integration examples")
    parser.add_argument("--address", help="BLE device address")
    parser.add_argument(
        "--check-libraries", action="store_true", help="Check available libraries"
    )
    args = parser.parse_args()

    if args.check_libraries:
        libraries = setup_library_check()
        print("Available BLE Libraries:")
        for lib, available in libraries.items():
            status = "✓" if available else "✗"
            print(f"  {status} {lib}")
    elif args.address:
        await demo_bleak_integration(args.address)
        print()
        await demo_device_integration(args.address)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
