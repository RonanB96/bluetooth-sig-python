#!/usr/bin/env python3
"""Service discovery example using the Device class.

Demonstrates how to discover services and characteristics using the
Bluetooth SIG translator together with a pluggable connection manager.
"""

import asyncio
from typing import cast


async def main() -> None:
    """Main function for service discovery demonstration."""
    # Use common argparse utilities
    from examples.utils import create_common_parser, create_connection_manager, validate_and_setup

    parser = create_common_parser("Service discovery with Device class")
    args = parser.parse_args()
    common_args = validate_and_setup(args)

    # Create connection manager using the common factory
    connection_manager = create_connection_manager(common_args.connection_manager, common_args.address)

    # Runtime imports
    from examples.utils.demo_functions import demo_service_discovery

    # Address is guaranteed to be non-None since require_address=True
    address = cast(str, common_args.address)
    await demo_service_discovery(address, connection_manager)


if __name__ == "__main__":
    asyncio.run(main())
