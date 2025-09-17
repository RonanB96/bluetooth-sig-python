#!/usr/bin/env python3
"""Notification handling example."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared_utils import demo_notifications


async def main():
    """Main function for notification demonstration."""
    parser = argparse.ArgumentParser(description="BLE notification handling")
    parser.add_argument("--address", required=True, help="BLE device address")
    parser.add_argument(
        "--characteristic", required=True, help="Characteristic UUID for notifications"
    )
    args = parser.parse_args()

    await demo_notifications(args.address, args.characteristic)


if __name__ == "__main__":
    asyncio.run(main())
