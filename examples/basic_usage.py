#!/usr/bin/env python3
"""Basic usage example for bluetooth_sig library."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared_utils import demo_basic_usage


async def main():
    """Main function for basic usage demonstration."""
    parser = argparse.ArgumentParser(description="Basic bluetooth_sig usage")
    parser.add_argument("--address", required=True, help="BLE device address")
    args = parser.parse_args()

    await demo_basic_usage(args.address)


if __name__ == "__main__":
    asyncio.run(main())
