#!/usr/bin/env python3
"""Service discovery example using the Device class.

Demonstrates how to discover services and characteristics using the
Bluetooth SIG translator together with a pluggable connection manager.
"""

# Set up paths for imports
import sys
from pathlib import Path

# pylint: disable=duplicate-code

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add parent directory for examples package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add examples directory for utils imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import asyncio

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from examples.shared_utils import demo_service_discovery

try:
    from examples.utils.bleak_retry_integration import BleakRetryConnectionManager
    from examples.utils.simpleble_integration import SimplePyBLEConnectionManager

    simplepyble_available = True
except ImportError:
    from examples.utils.bleak_retry_integration import BleakRetryConnectionManager

    simplepyble_available = False


async def main() -> None:
    """Main function for service discovery demonstration."""
    # pylint: disable=duplicate-code
    # NOTE: Argument parsing duplicates basic_usage.py CLI setup.
    # Duplication justified because:
    # 1. Each example script is self-contained for educational clarity
    # 2. Users should be able to run examples independently without shared CLI module
    # 3. Different examples may diverge in their specific arguments over time
    parser = argparse.ArgumentParser(description="Service discovery with Device class")
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

    await demo_service_discovery(args.address, connection_manager)


if __name__ == "__main__":
    asyncio.run(main())
