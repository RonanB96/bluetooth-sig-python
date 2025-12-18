#!/usr/bin/env python3
"""Nordic Thingy:52 example using bluetooth-sig-python library with real device.

This example demonstrates how to extend the bluetooth-sig-python library
for vendor-specific characteristics while maintaining the unified API.


Usage:
    # Read all sensors
    python thingy52_example.py AA:BB:CC:DD:EE:FF

    # Read specific sensors
    python thingy52_example.py AA:BB:CC:DD:EE:FF --temperature --humidity --battery

References:
    - Nordic Thingy:52 Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
    - BluePy Library: https://github.com/IanHarvey/bluepy
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.gatt.exceptions import BluetoothSIGError
from bluetooth_sig.types.uuid import BluetoothUUID

# Import connection manager from parent directory
from examples.connection_managers.bluepy import BluePyConnectionManager

# Import our custom characteristics from current package
from .thingy52_characteristics import (
    NORDIC_UUID_BASE,
)

logger = logging.getLogger(__name__)


async def read_thingy52_sensors(
    device: Device,
    connection_manager: BluePyConnectionManager,
    sensor_uuids: dict[str, str],
) -> dict[str, Any]:
    """Read sensors from Thingy:52 using unified Device API.

    This demonstrates the key benefit: both SIG and vendor characteristics
    are read through the same Device interface.

    Args:
        device: Device instance
        connection_manager: Connection manager
        sensor_uuids: Dictionary mapping sensor names to UUIDs

    Returns:
        Dictionary of sensor readings
    """
    results: dict[str, Any] = {}

    for sensor_name, uuid in sensor_uuids.items():
        try:
            # Read raw data from device
            raw_data = await connection_manager.read_gatt_char(BluetoothUUID(uuid))

            # Parse using registered characteristic (SIG or vendor)
            parsed = device.translator.parse_characteristic(uuid, raw_data)

            results[sensor_name] = parsed.value
            print(f"  {sensor_name:20s}: {parsed.value}")

        except BluetoothSIGError as e:
            # Catch Bluetooth SIG parsing/validation errors
            results[sensor_name] = f"Error: {e}"
            print(f"  {sensor_name:20s}: Error - {e}")
        except OSError as e:
            # Catch connection/communication errors from BluePy
            results[sensor_name] = f"Error: {e}"
            print(f"  {sensor_name:20s}: Error - {e}")

    return results


def build_sensor_list(args: argparse.Namespace) -> dict[str, str]:
    """Build sensor UUID list based on command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Dictionary mapping sensor names to UUIDs
    """
    sensor_uuids: dict[str, str] = {}

    # Map argument flags to sensor definitions
    sensor_map = {
        "battery": ("Battery Level (SIG)", "2A19"),
        "temperature": ("Temperature", NORDIC_UUID_BASE % 0x0201),
        "pressure": ("Pressure", NORDIC_UUID_BASE % 0x0202),
        "humidity": ("Humidity", NORDIC_UUID_BASE % 0x0203),
        "gas": ("Gas (eCO2/TVOC)", NORDIC_UUID_BASE % 0x0204),
        "color": ("Color (RGBC)", NORDIC_UUID_BASE % 0x0205),
        "button": ("Button", NORDIC_UUID_BASE % 0x0302),
        "orientation": ("Orientation", NORDIC_UUID_BASE % 0x0403),
        "heading": ("Heading", NORDIC_UUID_BASE % 0x0409),
    }

    # Add sensors based on flags
    for flag, (name, uuid) in sensor_map.items():
        if args.all or getattr(args, flag, False):
            sensor_uuids[name] = uuid

    return sensor_uuids


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nordic Thingy:52 example using bluetooth-sig-python library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("address", help="BLE MAC address of Thingy:52 (format: AA:BB:CC:DD:EE:FF)")
    parser.add_argument("--battery", action="store_true", help="Read battery level (SIG)")
    parser.add_argument("--temperature", action="store_true", help="Read temperature (Nordic vendor)")
    parser.add_argument("--pressure", action="store_true", help="Read pressure (Nordic vendor)")
    parser.add_argument("--humidity", action="store_true", help="Read humidity (Nordic vendor)")
    parser.add_argument("--gas", action="store_true", help="Read gas sensor (Nordic vendor)")
    parser.add_argument("--color", action="store_true", help="Read color sensor (Nordic vendor)")
    parser.add_argument("--button", action="store_true", help="Read button state (Nordic vendor)")
    parser.add_argument("--orientation", action="store_true", help="Read orientation (Nordic vendor)")
    parser.add_argument("--heading", action="store_true", help="Read heading (Nordic vendor)")
    parser.add_argument("--all", action="store_true", help="Read all sensors")

    args = parser.parse_args()

    # If no specific sensors selected, read all
    if not any(
        [
            args.battery,
            args.temperature,
            args.pressure,
            args.humidity,
            args.gas,
            args.color,
            args.button,
            args.orientation,
            args.heading,
            args.all,
        ]
    ):
        args.all = True

    # Initialize translator and device
    translator = BluetoothSIGTranslator()
    device = Device(args.address, translator)

    # Create connection manager (reusable BluePy adapter)
    connection_manager = BluePyConnectionManager(args.address)
    device.connection_manager = connection_manager

    try:
        # Connect to device
        await connection_manager.connect()
        print(f"✅ Connected to {args.address}\n")

        # Build sensor list based on arguments
        sensor_uuids = build_sensor_list(args)

        # Read sensors
        print(f"{'=' * 70}")
        print("Nordic Thingy:52 Sensor Readings")
        print(f"{'=' * 70}\n")

        results = await read_thingy52_sensors(device, connection_manager, sensor_uuids)

        print(f"\n{'=' * 70}")
        print(f"✅ Successfully read {len([v for v in results.values() if not isinstance(v, str)])} sensors")
        print(f"{'=' * 70}\n")

        # Disconnect
        await connection_manager.disconnect()

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        await connection_manager.disconnect()
        return 0

    except (OSError, RuntimeError) as e:
        # Catch BluePy connection errors and runtime errors
        print(f"\n❌ Error: {e}")
        if connection_manager.is_connected:
            await connection_manager.disconnect()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
