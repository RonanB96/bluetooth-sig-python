#!/usr/bin/env python3
"""Notification handling example using generic connection manager support.

This example demonstrates how to subscribe and handle BLE notifications
using any supported connection manager (bleak-retry, simplepyble, etc.).
"""

import asyncio


async def main() -> None:
    """Main function for notification demonstration."""
    # Use common argparse utilities
    from examples.utils import (
        create_common_parser,
        create_connection_manager,
        handle_notifications_generic,
        validate_and_setup,
    )

    parser = create_common_parser("BLE notification handling")
    parser.add_argument("--characteristic", required=True, help="Characteristic UUID for notifications")
    parser.add_argument("--duration", type=int, default=10, help="Duration to listen in seconds")
    args = parser.parse_args()
    common_args = validate_and_setup(args)

    # Create connection manager using the common factory
    connection_manager = create_connection_manager(common_args.connection_manager, common_args.address)
    await connection_manager.connect()

    # Handle notifications using the generic handler
    await handle_notifications_generic(connection_manager, args.characteristic, args.duration)


if __name__ == "__main__":
    asyncio.run(main())
