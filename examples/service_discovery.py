#!/usr/bin/env python3
# Set up paths for imports
import sys
from pathlib import Path

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add parent directory for examples package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add examples directory for utils imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import asyncio

from examples.shared_utils import demo_service_discovery

"""Service discovery example using Device class."""


async def main() -> None:
    """Main function for service discovery demonstration."""
    parser = argparse.ArgumentParser(description="Service discovery with Device class")
    parser.add_argument("--address", required=True, help="BLE device address")
    args = parser.parse_args()

    await demo_service_discovery(args.address)


if __name__ == "__main__":
    asyncio.run(main())
