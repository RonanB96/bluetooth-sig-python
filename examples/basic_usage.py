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

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from examples.shared_utils import demo_basic_usage

try:
    from examples.utils.bleak_retry_integration import BleakRetryConnectionManager
    from examples.utils.simpleble_integration import SimplePyBLEConnectionManager

    simplepyble_available = True
except ImportError:
    from examples.utils.bleak_retry_integration import BleakRetryConnectionManager

    simplepyble_available = False

"""Basic usage example for bluetooth_sig library."""


async def main() -> None:
    """Main function for basic usage demonstration."""
    parser = argparse.ArgumentParser(description="Basic bluetooth_sig usage")
    parser.add_argument("--address", required=True, help="BLE device address")
    parser.add_argument(
        "--connection-manager",
        choices=["bleak-retry", "simplepyble"],
        default="bleak-retry",
        help="BLE connection manager to use (default: bleak-retry)",
    )
    args = parser.parse_args()

    # Create connection manager based on choice
    connection_manager: ConnectionManagerProtocol
    if args.connection_manager == "simplepyble":
        if not simplepyble_available:
            print("SimplePyBLE not available. Install with: pip install simplepyble")
            return
        import simplepyble  # type: ignore[import-untyped]

        connection_manager = SimplePyBLEConnectionManager(args.address, simplepyble)
    else:
        connection_manager = BleakRetryConnectionManager(args.address)

    await demo_basic_usage(args.address, connection_manager)


if __name__ == "__main__":
    asyncio.run(main())
