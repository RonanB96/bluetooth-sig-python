#!/usr/bin/env python3
"""Basic usage example for the bluetooth_sig library."""

from __future__ import annotations

import argparse
import asyncio

from bluetooth_sig.device.connection import ConnectionManagerProtocol


async def main() -> None:
    """Main function for basic usage demonstration."""
    # Runtime imports (may raise ImportError if optional extras are missing)
    from examples.utils.demo_functions import demo_basic_usage as demo_basic_usage_fn

    try:
        from examples.connection_managers.bleak_retry import BleakRetryConnectionManager
        from examples.connection_managers.simpleble import SimplePyBLEConnectionManager

        simplepyble_available = True
    except ImportError:
        from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

        simplepyble_available = False
    # pylint: disable=duplicate-code
    # NOTE: Argument parsing duplicates service_discovery.py CLI setup.
    # Duplication justified because:
    # 1. Each example script is self-contained for educational clarity
    # 2. Users should be able to run examples independently without shared CLI module
    # 3. Different examples may diverge in their specific arguments over time
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

    await demo_basic_usage_fn(args.address, connection_manager)


if __name__ == "__main__":
    asyncio.run(main())
