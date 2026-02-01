#!/usr/bin/env python3
"""Common argparse utilities for BLE examples.

This module provides shared argument parsing and connection manager
selection logic to reduce duplication across examples.
"""

from __future__ import annotations

import argparse

from bluetooth_sig.device.connection import ConnectionManagerProtocol

from .library_detection import AVAILABLE_LIBRARIES, show_library_availability


class CommonArgs:
    """Common argument namespace for BLE examples."""

    def __init__(
        self,
        address: str | None = None,
        connection_manager: str = "auto",
        **kwargs: object,
    ) -> None:
        """Initialize common arguments.

        Args:
            address: BLE device address
            connection_manager: Connection manager to use ('auto', 'bleak-retry', 'simplepyble', etc.)
            **kwargs: Additional example-specific arguments
        """
        self.address = address
        self.connection_manager = connection_manager
        # Store any additional arguments
        for key, value in kwargs.items():
            setattr(self, key, value)


def create_common_parser(
    description: str,
    require_address: bool = False,
    add_connection_manager: bool = False,
) -> argparse.ArgumentParser:
    """Create a parser with common BLE example arguments.

    Args:
        description: Description for the argument parser
        require_address: Whether to add --address argument (required when added)
        add_connection_manager: Whether to add connection manager selection argument

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description=description)

    if require_address:
        parser.add_argument(
            "--address",
            "-a",
            required=True,
            help="BLE device address (e.g., '12:34:56:78:9A:BC')",
        )

    if add_connection_manager:
        # Get available connection managers
        available_managers = list(AVAILABLE_LIBRARIES.keys())
        if not available_managers:
            default_manager = "none"
            choices = ["none"]
        else:
            default_manager = available_managers[0]  # Use first available as default
            choices = available_managers

        parser.add_argument(
            "--connection-manager",
            "-c",
            choices=choices,
            default=default_manager,
            help=f"BLE connection manager to use (default: {default_manager})",
        )

    return parser


def create_connection_manager(
    manager_name: str,
    address: str | None,
) -> ConnectionManagerProtocol:
    """Create a connection manager instance based on name.

    Args:
        manager_name: Name of the connection manager ('bleak-retry', 'simplepyble', etc.)
        address: BLE device address (required, cannot be None)

    Returns:
        ConnectionManagerProtocol instance

    Raises:
        ValueError: If manager is not available, not supported, or address is None
        ImportError: If required dependencies are not installed
    """
    if address is None:
        raise ValueError("Device address is required for connection manager")

    if manager_name not in AVAILABLE_LIBRARIES:
        available = list(AVAILABLE_LIBRARIES.keys())
        raise ValueError(
            f"Connection manager '{manager_name}' not available. "
            f"Available: {available}. "
            f"Install with: pip install .[examples]"
        )

    if manager_name == "bleak-retry":
        from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

        return BleakRetryConnectionManager(address)

    if manager_name == "simplepyble":

        from examples.connection_managers.simpleble import SimplePyBLEConnectionManager

        return SimplePyBLEConnectionManager(address)

    if manager_name == "bluepy":
        from examples.connection_managers.bluepy import BluePyConnectionManager

        return BluePyConnectionManager(address)

    if manager_name == "bleak":
        # Basic bleak without retry logic
        from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

        # For now, just use the retry version - could add a basic bleak version later
        return BleakRetryConnectionManager(address)

    raise ValueError(f"Unsupported connection manager: {manager_name}")


def validate_and_setup(args: argparse.Namespace) -> CommonArgs:
    """Validate arguments and set up common args with connection manager.

    Args:
        args: Parsed command line arguments

    Returns:
        CommonArgs instance with validated setup

    Raises:
        SystemExit: If validation fails
    """
    # Check if any BLE libraries are available
    if not AVAILABLE_LIBRARIES:
        print("❌ No BLE libraries available!")
        print("Install example dependencies with: pip install .[examples]")
        print("\nAvailable libraries:")
        show_library_availability()
        raise SystemExit(1)

    # Get the selected connection manager
    manager_name = getattr(args, "connection_manager", "auto")
    if manager_name == "auto":
        # Auto-select the first available
        manager_name = list(AVAILABLE_LIBRARIES.keys())[0]

    # Validate the connection manager is available
    if manager_name not in AVAILABLE_LIBRARIES:
        print(f"❌ Connection manager '{manager_name}' not available!")
        print("Available managers:")
        for name, info in AVAILABLE_LIBRARIES.items():
            print(f"  - {name}: {info['description']}")
        raise SystemExit(1)

    # Create CommonArgs instance
    common_args = CommonArgs(
        address=getattr(args, "address", None),
        connection_manager=manager_name,
    )

    # Copy any additional attributes from args
    for attr in dir(args):
        if not attr.startswith("_") and not hasattr(common_args, attr):
            setattr(common_args, attr, getattr(args, attr))

    return common_args


__all__ = [
    "CommonArgs",
    "create_common_parser",
    "create_connection_manager",
    "validate_and_setup",
]
