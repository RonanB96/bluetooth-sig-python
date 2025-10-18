#!/usr/bin/env python3
"""Notification handling example using bleak-retry integration.

This example demonstrates how to subscribe and handle BLE notifications
using the bleak-retry-connector integration layered with the
bluetooth_sig parsing utilities.
"""

# Set up paths for imports
import sys
from pathlib import Path

# pylint: disable=duplicate-code

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add parent directory for examples package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add examples directory for utils imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import asyncio

from examples.utils.bleak_retry_integration import handle_notifications_bleak_retry


async def main() -> None:
    """Main function for notification demonstration."""
    parser = argparse.ArgumentParser(description="BLE notification handling")
    parser.add_argument("--address", required=True, help="BLE device address")
    parser.add_argument("--characteristic", required=True, help="Characteristic UUID for notifications")
    parser.add_argument("--duration", type=int, default=10, help="Duration to listen in seconds")
    args = parser.parse_args()

    await handle_notifications_bleak_retry(args.address, args.characteristic, duration=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
