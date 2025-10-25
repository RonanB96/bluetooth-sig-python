#!/usr/bin/env python3
"""Basic usage example for the bluetooth_sig library."""

from __future__ import annotations

import asyncio
from typing import cast


async def main() -> None:
    """Main function for basic usage demonstration."""
    # Use common argparse utilities
    from examples.utils import create_common_parser, create_connection_manager, validate_and_setup

    parser = create_common_parser("Basic bluetooth_sig usage")
    args = parser.parse_args()
    common_args = validate_and_setup(args)

    # Create connection manager using the common factory
    connection_manager = create_connection_manager(common_args.connection_manager, common_args.address)

    # Runtime imports
    from examples.utils.demo_functions import demo_basic_usage as demo_basic_usage_fn

    # Address is guaranteed to be non-None since require_address=True
    address = cast(str, common_args.address)
    await demo_basic_usage_fn(address, connection_manager)


if __name__ == "__main__":
    asyncio.run(main())
