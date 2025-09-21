#!/usr/bin/env python3
"""Service discovery example using Device class."""

import argparse
import asyncio

from .shared_utils import demo_service_discovery


async def main() -> None:
    """Main function for service discovery demonstration."""
    parser = argparse.ArgumentParser(description="Service discovery with Device class")
    parser.add_argument("--address", required=True, help="BLE device address")
    args = parser.parse_args()

    await demo_service_discovery(args.address)


if __name__ == "__main__":
    asyncio.run(main())
