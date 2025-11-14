# Usage

To use Bluetooth SIG Standards Library in a project:

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName

# Create translator instance
translator = BluetoothSIGTranslator()

# Resolve UUIDs / names to get information
service_info = translator.get_sig_info_by_name("Battery Service")
char_uuid = CharacteristicName.BATTERY_LEVEL.get_uuid()
char_info = translator.get_sig_info_by_uuid(char_uuid)

print(f"Service: {service_info.name}")
print(f"Characteristic: {char_info.name}")
```

## Basic Example

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName

def main():
    translator = BluetoothSIGTranslator()

    # UUID resolution
    uuid_info = translator.get_sig_info_by_uuid("180F")
    print(f"UUID 180F: {uuid_info.name}")

    # Name resolution
    name_info = translator.get_sig_info_by_name("Battery Level")
    print(f"Battery Level UUID: {name_info.uuid}")

    # Data parsing
    battery_uuid = CharacteristicName.BATTERY_LEVEL.get_uuid()
    parsed = translator.parse_characteristic(battery_uuid, bytearray([85]))
    print(f"Battery level: {parsed.value}%")


if __name__ == "__main__":
    main()
```

For more basic usage examples, see the [Quick Start Guide](quickstart.md).

### Async Usage

If you are using an async BLE client (for example, bleak), you can await async wrappers without changing parsing logic:

```python
from bluetooth_sig.core.async_translator import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = await translator.parse_characteristic_async("2A19", bytes([85]))
```

Prefer the existing examples for full context: see `examples/async_ble_integration.py`. The async classes are also documented in the Core API via mkdocstrings: `BluetoothSIGTranslator` and `AsyncParsingSession`.

## Real-World Usage Patterns

### Pattern 1: Fitness Tracker (Heart Rate + Battery)

Common in: Polar sensors, Fitbit devices, smartwatches

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName
from bleak import BleakClient

translator = BluetoothSIGTranslator()

async def monitor_fitness_device(address: str):
    async with BleakClient(address) as client:
        # Read battery level
        battery_uuid = CharacteristicName.BATTERY_LEVEL.get_uuid()
        battery_data = await client.read_gatt_char(battery_uuid)
        battery = translator.parse_characteristic(battery_uuid, battery_data)
        print(f"Battery: {battery.value}%")

        # Subscribe to heart rate notifications
        hr_uuid = CharacteristicName.HEART_RATE_MEASUREMENT.get_uuid()

        def heart_rate_callback(sender, data: bytearray):
            hr = translator.parse_characteristic(hr_uuid, data)
            if hr.parse_success:
                hr_data = hr.value
                print(f"Heart Rate: {hr_data.heart_rate} bpm")
                if hr_data.rr_intervals:
                    print(f"HRV: {hr_data.rr_intervals} seconds")

        await client.start_notify(hr_uuid, heart_rate_callback)
        await asyncio.sleep(30)  # Monitor for 30 seconds
```

### Pattern 2: Environmental Sensor Dashboard

Common in: Xiaomi sensors, SwitchBot meters, Govee hygrometers

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName

translator = BluetoothSIGTranslator()

async def read_environmental_sensors(devices: list[str]):
    """Read temp/humidity from multiple sensors"""
    for address in devices:
        async with BleakClient(address) as client:
            # Batch read multiple characteristics
            temp_uuid = CharacteristicName.TEMPERATURE.get_uuid()
            humidity_uuid = CharacteristicName.HUMIDITY.get_uuid()
            battery_uuid = CharacteristicName.BATTERY_LEVEL.get_uuid()

            temp_data = await client.read_gatt_char(temp_uuid)
            humidity_data = await client.read_gatt_char(humidity_uuid)
            battery_data = await client.read_gatt_char(battery_uuid)

            results = translator.parse_characteristics({
                temp_uuid: temp_data,
                humidity_uuid: humidity_data,
                battery_uuid: battery_data,
            })

            print(f"Sensor {address}:")
            print(f"  Temp: {results[temp_uuid].value}°C")
            print(f"  Humidity: {results[humidity_uuid].value}%")
            print(f"  Battery: {results[battery_uuid].value}%")
```

### Pattern 3: Medical Device (Blood Pressure Monitor)

Common in: Omron blood pressure monitors, A&D medical devices, iHealth monitors

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName
from bluetooth_sig.stream.pairing import DependencyPairingBuffer

translator = BluetoothSIGTranslator()

async def monitor_blood_pressure(address: str):
    """
    Blood pressure monitors send paired characteristics:
    - Blood Pressure Measurement (0x2A35)
    - Intermediate Cuff Pressure (0x2A36)

    These arrive out-of-order and may interleave from multiple measurement sessions.
    The pairing buffer groups them by timestamp automatically.
    """
    async with BleakClient(address) as client:
        completed_readings = []

        def on_complete_reading(paired_data: dict[str, CharacteristicData]):
            """Called when both BPM and ICP arrive for a timestamp"""
            bpm = paired_data[CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid()]
            icp = paired_data[CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid()]

            print(f"Reading at {bpm.value.timestamp}:")
            print(f"  Final: {bpm.value.systolic}/{bpm.value.diastolic} mmHg")
            print(f"  Peak cuff: {icp.value.systolic} mmHg")
            completed_readings.append(paired_data)

        # Create pairing buffer that groups by timestamp
        buffer = DependencyPairingBuffer(
            translator=translator,
            required_uuids={
                CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid(),
                CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid(),
            },
            group_key=lambda data: data.value.timestamp if hasattr(data.value, 'timestamp') else None,
            on_pair=on_complete_reading
        )

        # Subscribe to both characteristics
        bpm_uuid = CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid()
        icp_uuid = CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid()

        await client.start_notify(bpm_uuid, lambda _, data: buffer.ingest(bpm_uuid, data))
        await client.start_notify(icp_uuid, lambda _, data: buffer.ingest(icp_uuid, data))

        await asyncio.sleep(60)  # Monitor for 1 minute

        print(f"\nCollected {len(completed_readings)} complete readings")
```

## Dependency-Aware Batch Parsing (Recommended)

When multiple characteristics are related (e.g., Blood Pressure Measurement `0x2A35` and Intermediate Cuff Pressure `0x2A36`), parse them together so the translator can handle them correctly.

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName

translator = BluetoothSIGTranslator()

# Raw values obtained from your BLE stack (notifications or reads)
bpm_uuid = CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid()
icp_uuid = CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid()

char_data = {
    bpm_uuid: blood_pressure_measurement_bytes,
    icp_uuid: intermediate_cuff_pressure_bytes,
}

# Optionally include descriptors: {char_uuid: {descriptor_uuid: raw_bytes}}
descriptor_data = {}

results = translator.parse_characteristics(char_data, descriptor_data=descriptor_data)

bpm = results[bpm_uuid].value   # Parsed BloodPressureMeasurementData
icp = results[icp_uuid].value   # Parsed IntermediateCuffPressureData

print(f"Blood Pressure: {bpm.systolic}/{bpm.diastolic} mmHg at {bpm.timestamp}")
print(f"Peak Cuff Pressure: {icp.systolic} mmHg at {icp.timestamp}")
```

This batch API is the most user-friendly path: you provide UUIDs and raw bytes; the library parses each characteristic according to its specification.

## Strongly-Typed Raw Input Containers

If you prefer typed containers before calling the translator, use these types:

- `bluetooth_sig.types.io.RawCharacteristicRead` — holds a single read (`uuid`, `raw_data`, optional `descriptors`, optional `properties`).
- `bluetooth_sig.types.io.RawCharacteristicBatch` — a batch of reads.
- `bluetooth_sig.types.io.to_parse_inputs(batch)` — converts a batch to the exact `(char_data, descriptor_data)` shapes accepted by `parse_characteristics`.

Example:

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName
from bluetooth_sig.types.io import RawCharacteristicRead, RawCharacteristicBatch, to_parse_inputs

bpm_uuid = CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid()
icp_uuid = CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid()

batch = RawCharacteristicBatch(
    items=[
        RawCharacteristicRead(uuid=bpm_uuid, raw_data=blood_pressure_measurement_bytes),
        RawCharacteristicRead(uuid=icp_uuid, raw_data=intermediate_cuff_pressure_bytes),
    ]
)

char_data, descriptor_data = to_parse_inputs(batch)
results = BluetoothSIGTranslator().parse_characteristics(char_data, descriptor_data=descriptor_data)
```

## Converting Bleak/SimpleBLE Data

Example adapters for common connection managers are available in their respective files:

- `bleak_services_to_batch()` in `examples/connection_managers/bleak_utils.py`
- `simpleble_services_to_batch()` in `examples/connection_managers/simpleble.py`

These helpers use duck typing to avoid introducing BLE backend dependencies into the core library.

Usage sketch with Bleak:

```python
# Pseudocode — assumes you already used Bleak to discover services and read values
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.io import to_parse_inputs
from examples.connection_managers.bleak_utils import bleak_services_to_batch

services = await client.get_services()  # BleakGATTServiceCollection

# Build a map of values you already read, e.g. from notifications or reads
from bluetooth_sig import CharacteristicName
bpm_uuid = CharacteristicName.BLOOD_PRESSURE_MEASUREMENT.get_uuid()
icp_uuid = CharacteristicName.INTERMEDIATE_CUFF_PRESSURE.get_uuid()

values = {
    bpm_uuid: bpm_bytes,
    icp_uuid: icp_bytes,
}

batch = bleak_services_to_batch(services, values_by_uuid=values)
char_data, descriptor_data = to_parse_inputs(batch)
results = BluetoothSIGTranslator().parse_characteristics(char_data, descriptor_data=descriptor_data)
```

The SimpleBLE variant follows the same pattern:

```python
from examples.connection_managers.simpleble import simpleble_services_to_batch

batch = simpleble_services_to_batch(services, values_by_uuid=values)
char_data, descriptor_data = to_parse_inputs(batch)
results = BluetoothSIGTranslator().parse_characteristics(char_data, descriptor_data=descriptor_data)
```

These helpers align with what Bleak and SimpleBLE typically expose: service collections with characteristic entries (`uuid`, optional `properties`, optional `descriptors`). They avoid making network calls; provide `values_by_uuid` from your reads/notifications. Example adapters live under `examples/connection_managers/` and may need updates to match your backend versions—copy and tweak as needed.

For a step-by-step porting overview (before/after), see the [Migration Guide](guides/migration.md).

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
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName
from bluetooth_sig.device import Device

async def main():
    # Create translator and device
    translator = BluetoothSIGTranslator()
    device = Device("AA:BB:CC:DD:EE:FF", translator)

    # Parse advertisement data
    adv_data = bytes([
        0x0C, 0x09, 0x54, 0x65, 0x73, 0x74, 0x20, 0x44, 0x65, 0x76, 0x69, 0x63, 0x65,  # Local Name
    ])
    device.parse_advertiser_data(adv_data)
    print(f"Device name: {device.name}")

    # Discover services (real workflow with connection manager)
    await device.discover_services()

    # Read characteristic data using high-level enum
    battery_uuid = CharacteristicName.BATTERY_LEVEL.get_uuid()
    battery_level = await device.read(battery_uuid)
    print(f"Battery level: {battery_level.value}%")

    # Check encryption requirements
    print(f"Requires encryption: {device.encryption.requires_encryption}")
    print(f"Requires authentication: {device.encryption.requires_authentication}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Device with BLE Connection Library

The Device class integrates with any BLE connection library:

```python
import asyncio
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicName
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
            for char in service.characteristics:
                # Read characteristic value using device.read()
                # Convert UUID string to BluetoothUUID
                char_uuid = BluetoothUUID(char.uuid)
                char_data = await device.read(char_uuid)
                print(f"Characteristic {char.uuid}: {char_data.value}")

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
