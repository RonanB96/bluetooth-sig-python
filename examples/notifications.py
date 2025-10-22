#!/usr/bin/env python3
"""Notification handling example using bleak-retry integration.

This example demonstrates how to subscribe and handle BLE notifications
using the bleak-retry-connector integration layered with the
bluetooth_sig parsing utilities.
"""

import argparse
import asyncio


async def main() -> None:
    """Main function for notification demonstration."""
    from examples.connection_managers.bleak_utils import handle_notifications_bleak_retry

    parser = argparse.ArgumentParser(description="BLE notification handling")
    parser.add_argument("--address", required=True, help="BLE device address")
    parser.add_argument("--characteristic", required=True, help="Characteristic UUID for notifications")
    parser.add_argument("--duration", type=int, default=10, help="Duration to listen in seconds")
    args = parser.parse_args()

    await handle_notifications_bleak_retry(args.address, args.characteristic, duration=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
