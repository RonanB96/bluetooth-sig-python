# Usage

To use Bluetooth SIG Standards Library in a project:

```python
from bluetooth_sig import BluetoothSIGTranslator

# Create translator instance
translator = BluetoothSIGTranslator()

# Resolve UUIDs to get information
service_info = translator.get_sig_info_by_uuid("180F")  # Battery Service
char_info = translator.get_sig_info_by_uuid("2A19")    # Battery Level

print(f"Service: {service_info.name}")
print(f"Characteristic: {char_info.name}")
```

## Basic Example

```python
from bluetooth_sig import BluetoothSIGTranslator

def main():
    translator = BluetoothSIGTranslator()

    # UUID resolution
    uuid_info = translator.get_sig_info_by_uuid("180F")
    print(f"UUID 180F: {uuid_info.name}")

    # Name resolution
    name_info = translator.get_sig_info_by_name("Battery Level")
    print(f"Battery Level UUID: {name_info.uuid}")

    # Data parsing
    parsed = translator.parse_characteristic("2A19", bytearray([85]))
    print(f"Battery level: {parsed.value}%")


if __name__ == "__main__":
    main()
```

For more basic usage examples, see the [Quick Start Guide](quickstart.md).

______________________________________________________________________

## Troubleshooting

If you encounter errors when parsing characteristic data (e.g., unknown UUID, insufficient data, or value out of range), check:

- The UUID and data format match the official specification
- Your data is a bytearray of the correct length

See the [Testing Guide](testing.md) for more on validating your setup and troubleshooting parsing issues.

## Device Class

The `Device` class provides a high-level abstraction for grouping BLE device services, characteristics, encryption requirements, and advertiser data. It serves as a pure SIG standards translator, not a BLE connection manager.

### Basic Device Usage

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device

def main():
    # Create translator and device
    translator = BluetoothSIGTranslator()
    device = Device("AA:BB:CC:DD:EE:FF", translator)

    # Parse advertisement data
    adv_data = bytes([
        0x0C, 0x09, 0x54, 0x65, 0x73, 0x74, 0x20, 0x44, 0x65, 0x76, 0x69, 0x63, 0x65,  # Local Name
    ])
    device.parse_advertiser_data(adv_data)
    print(f"Device name: {device.name}")

    # Add services with characteristics
    battery_service = {
        "2A19": b'\x64',  # Battery Level: 100%
    }
    device.add_service("180F", battery_service)

    # Access parsed characteristic data
    battery_level = device.get_characteristic_data("180F", "2A19")
    print(f"Battery level: {battery_level.value}%")

    # Check encryption requirements
    print(f"Requires encryption: {device.encryption.requires_encryption}")
    print(f"Requires authentication: {device.encryption.requires_authentication}")

if __name__ == "__main__":
    main()
```

### Device with BLE Connection Library

The Device class integrates with any BLE connection library:

```python
import asyncio
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device

async def discover_device(device_address):
    translator = BluetoothSIGTranslator()
    device = Device(device_address, translator)

    async with BleakClient(device_address) as client:
        # Get advertisement data (if available from your BLE library)
        # device.parse_advertiser_data(advertisement_bytes)

        # Discover services
        services = await client.get_services()

        for service in services:
            # Collect characteristics for this service
            char_data = {}
            for char in service.characteristics:
                # Read characteristic value
                value = await client.read_gatt_char(char.uuid)
                char_data[char.uuid] = value

            # Add service to device
            device.add_service(service.uuid, char_data)

    # Now you have a complete device representation
    print(f"Device: {device}")
    for service_uuid, service_data in device.services.items():
        print(f"Service {service_uuid}: {len(service_data.characteristics)} characteristics")

    return device
```

### Device Data Structures

The Device class uses several data structures:

- `DeviceService`: Groups a service with its parsed characteristics
- `DeviceEncryption`: Tracks encryption and authentication requirements
- `DeviceAdvertiserData`: Parsed advertisement data including manufacturer info, service UUIDs, etc.

All data structures follow the Bluetooth SIG specifications and provide type-safe access to device information.
