#!/usr/bin/env python3
"""Advertising data parsing example."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared_utils import demo_advertising_parsing


async def main():
    """Main function for advertising parsing demonstration."""
    parser = argparse.ArgumentParser(description="BLE advertising data parsing")
    parser.add_argument("--data", required=True, help="Hex string of advertising data")
    args = parser.parse_args()

    # Convert hex string to bytes
    try:
        raw_data = bytes.fromhex(args.data.replace(" ", "").replace(":", ""))
    except ValueError:
        print("Invalid hex data provided")
        return

    await demo_advertising_parsing(raw_data)


if __name__ == "__main__":
    asyncio.run(main())
