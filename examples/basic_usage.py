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

from examples.shared_utils import demo_basic_usage

"""Basic usage example for bluetooth_sig library."""


async def main() -> None:
    """Main function for basic usage demonstration."""
    parser = argparse.ArgumentParser(description="Basic bluetooth_sig usage")
    parser.add_argument("--address", required=True, help="BLE device address")
    args = parser.parse_args()

    await demo_basic_usage(args.address)


if __name__ == "__main__":
    asyncio.run(main())
