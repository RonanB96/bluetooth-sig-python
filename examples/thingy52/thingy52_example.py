#!/usr/bin/env python3
"""Nordic Thingy:52 BLE sensor reading example.

This example demonstrates reading environmental sensors, UI elements,
and motion sensors from a Nordic Thingy:52 device using the
bluetooth-sig-python library.

The Thingy:52 uses vendor-specific characteristics that differ from
Bluetooth SIG standards, so custom characteristic classes are used.

Requirements:
    pip install bleak  # or bluepy, or simplepyble

Usage:
    python thingy52_example.py --address 12:34:56:78:9A:BC
    python thingy52_example.py --address 12:34:56:78:9A:BC --all
    python thingy52_example.py --address 12:34:56:78:9A:BC --temperature --pressure
    python thingy52_example.py --address 12:34:56:78:9A:BC --connection-manager bleak
"""

from __future__ import annotations

import argparse
import asyncio
import os
from typing import TYPE_CHECKING

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from examples.thingy52.thingy52_characteristics import (
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyGasCharacteristic,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)
from examples.utils.argparse_utils import create_connection_manager

if TYPE_CHECKING:
    pass


async def read_thingy_characteristic(device: Device, char_uuid: str, name: str) -> None:
    """Read and display a Thingy:52 characteristic.

    Args:
        device: Connected Device instance
        char_uuid: Characteristic UUID string
        name: Human-readable name for display
    """
    try:
        result = await device.read(char_uuid)
        print(f"✅ {name}: {result}")
    except Exception as e:
        print(f"❌ {name}: Failed to read - {e}")


async def demonstrate_thingy52_reading(address: str, sensors: list[str], connection_manager_name: str) -> None:
    """Demonstrate reading characteristics from a Nordic Thingy:52 device.

    Args:
        address: BLE device address
        sensors: List of sensor names to read
        connection_manager_name: Name of connection manager to use
    """
    print(f"🔍 Connecting to Thingy:52 at {address} using {connection_manager_name}...")

    # Initialize the translator
    translator = BluetoothSIGTranslator()

    # Register custom Thingy:52 characteristics
    translator.register_custom_characteristic_class(ThingyTemperatureCharacteristic)
    translator.register_custom_characteristic_class(ThingyPressureCharacteristic)
    translator.register_custom_characteristic_class(ThingyHumidityCharacteristic)
    translator.register_custom_characteristic_class(ThingyGasCharacteristic)
    translator.register_custom_characteristic_class(ThingyColorCharacteristic)
    translator.register_custom_characteristic_class(ThingyButtonCharacteristic)
    translator.register_custom_characteristic_class(ThingyOrientationCharacteristic)
    translator.register_custom_characteristic_class(ThingyHeadingCharacteristic)

    # Create device
    device = Device(address, translator)

    # Create and attach connection manager
    connection_manager = create_connection_manager(connection_manager_name, address)
    device.attach_connection_manager(connection_manager)

    try:
        # Connect to device
        await device.connect()
        print("✅ Connected to Thingy:52")

        # Read selected sensors
        if "temperature" in sensors or "all" in sensors:
            uuid = str(ThingyTemperatureCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Temperature")

        if "pressure" in sensors or "all" in sensors:
            uuid = str(ThingyPressureCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Pressure")

        if "humidity" in sensors or "all" in sensors:
            uuid = str(ThingyHumidityCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Humidity")

        if "gas" in sensors or "all" in sensors:
            uuid = str(ThingyGasCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Gas (eCO2/TVOC)")

        if "color" in sensors or "all" in sensors:
            uuid = str(ThingyColorCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Color")

        if "button" in sensors or "all" in sensors:
            uuid = str(ThingyButtonCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Button")

        if "orientation" in sensors or "all" in sensors:
            uuid = str(ThingyOrientationCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Orientation")

        if "heading" in sensors or "all" in sensors:
            uuid = str(ThingyHeadingCharacteristic.get_class_uuid() or "")
            await read_thingy_characteristic(device, uuid, "Heading")

    except Exception as e:
        print(f"❌ Operation failed: {e}")
    finally:
        # Always disconnect
        try:
            await device.disconnect()
            print("✅ Disconnected from Thingy:52")
        except Exception as e:
            print(f"⚠️  Disconnect failed: {e}")


def main() -> None:
    """Main function for Thingy:52 demonstration."""
    parser = argparse.ArgumentParser(description="Nordic Thingy:52 BLE sensor reading example")

    parser.add_argument("--address", "-a", required=True, help="Thingy:52 BLE device address (e.g., AA:BB:CC:DD:EE:FF)")
    parser.add_argument(
        "--connection-manager",
        "-c",
        choices=["bleak-retry", "bluepy", "simplepyble"],
        default=os.getenv("BLE_CONNECTION_MANAGER", "bleak-retry"),
        help="BLE connection manager to use (default: bleak-retry, or BLE_CONNECTION_MANAGER env var)",
    )

    # Sensor selection flags
    parser.add_argument("--temperature", "-t", action="store_true", help="Read temperature sensor")
    parser.add_argument("--pressure", "-p", action="store_true", help="Read pressure sensor")
    parser.add_argument("--humidity", action="store_true", help="Read humidity sensor")
    parser.add_argument("--gas", "-g", action="store_true", help="Read gas sensor (eCO2/TVOC)")
    parser.add_argument("--color", action="store_true", help="Read color sensor")
    parser.add_argument("--button", "-b", action="store_true", help="Read button state")
    parser.add_argument("--orientation", "-o", action="store_true", help="Read orientation sensor")
    parser.add_argument("--heading", action="store_true", help="Read heading sensor")
    parser.add_argument("--all", action="store_true", help="Read all sensors")

    args = parser.parse_args()

    # Determine which sensors to read
    sensors = []
    if args.all:
        sensors = ["all"]
    else:
        sensor_flags = [
            ("temperature", args.temperature),
            ("pressure", args.pressure),
            ("humidity", args.humidity),
            ("gas", args.gas),
            ("color", args.color),
            ("button", args.button),
            ("orientation", args.orientation),
            ("heading", args.heading),
        ]
        sensors = [name for name, flag in sensor_flags if flag]

    if not sensors:
        print("❌ No sensors selected!")
        print("Use --all or specify individual sensors (e.g., --temperature --pressure)")
        return

    print("🔵 Nordic Thingy:52 BLE Sensor Reading Example")
    print("=" * 50)
    print(f"Device: {args.address}")
    print(f"Connection Manager: {args.connection_manager}")
    print(f"Sensors: {', '.join(sensors)}")
    print()

    try:
        asyncio.run(demonstrate_thingy52_reading(args.address, sensors, args.connection_manager))
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
