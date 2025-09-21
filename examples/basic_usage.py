#!/usr/bin/env python3
"""Basic usage example for bluetooth_sig library."""

import argparse
import asyncio

from .shared_utils import demo_basic_usage


async def main() -> None:
    """Main function for basic usage demonstration."""
    parser = argparse.ArgumentParser(description="Basic bluetooth_sig usage")
    parser.add_argument("--address", required=True, help="BLE device address")
    args = parser.parse_args()

    await demo_basic_usage(args.address)


if __name__ == "__main__":
    asyncio.run(main())
