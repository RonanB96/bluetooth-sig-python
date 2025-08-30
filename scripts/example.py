"""Example script to demonstrate BLE GATT device functionality."""

import argparse
import asyncio

from path_config import configure_path

configure_path()

from ble_gatt_device import BLEGATTDevice  # noqa: E402


async def main(mac_address: str):
    """Main function to demonstrate BLE GATT device functionality.

    Args:
        mac_address: The MAC address of the BLE device to connect to
    """
    device = BLEGATTDevice(mac_address)

    try:
        print(f"Connecting to device {mac_address}...")
        if await device.connect():
            print("Connected successfully!")

            print("\nReading characteristics...")
            values = await device.read_characteristics()

            print("\nRead values:")
            for key, value in values.items():
                print(f"{key}: {value}")
        else:
            print("Failed to connect to device")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("\nDisconnecting...")
        await device.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read values from a BLE GATT device")
    parser.add_argument("mac_address", help="MAC address of the BLE device")
    args = parser.parse_args()

    asyncio.run(main(args.mac_address))
