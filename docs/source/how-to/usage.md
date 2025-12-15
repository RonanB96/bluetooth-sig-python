# Usage

**Key Principle**: You don't need to know Bluetooth UUIDs! This library automatically recognizes standard SIG characteristics and tells you what they are.

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_HEART_RATE_DATA = bytearray([72])  # Simulates 72 bpm heart rate
# Example UUID from your BLE library - in reality you'd get this from device discovery
UNKNOWN_UUID = (
    "2A37"  # Heart Rate Measurement - you don't know what this is yet!
)

# Create translator instance
translator = BluetoothSIGTranslator()

# Get UUID from your BLE library, let the translator identify it
result = translator.parse_characteristic(
    UNKNOWN_UUID, SIMULATED_HEART_RATE_DATA
)

# The library tells you what it is and parses it correctly
print(f"This UUID is: {result.info.name}")  # "Heart Rate Measurement"
print(f"Value: {result.value}")  # HeartRateData(heart_rate=72, ...)

# Alternative: If you know what characteristic you want, convert enum to UUID
hr_uuid = translator.get_characteristic_uuid_by_name(
    CharacteristicName.HEART_RATE_MEASUREMENT
)
if hr_uuid:
    result2 = translator.parse_characteristic(
        str(hr_uuid), SIMULATED_HEART_RATE_DATA
    )
    print(
        f"Heart Rate: {result2.value.heart_rate} bpm"
    )  # Same result - library resolves enum to UUID
```

## Basic Example: Understanding BLE Library Output

BLE libraries like bleak and simplepyble give you UUIDs in various formats. Here's what you actually receive and how to parse it:

```python
from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator


async def discover_device_characteristics(address: str):
    """Real-world example: What you get from bleak and how to parse it."""
    translator = BluetoothSIGTranslator()

    async with BleakClient(address) as client:
        # 1. Bleak gives you services - you don't know what they are
        services = await client.get_services()

        for service in services:
            # service.uuid is a string like "0000180f-0000-1000-8000-00805f9b34fb"
            # This is the full 128-bit UUID format
            print(f"\nService UUID: {service.uuid}")

            # Identify what this service is
            service_info = translator.get_sig_info_by_uuid(service.uuid)
            if service_info:
                print(f"  → Identified as: {service_info.name}")  # "Battery"

            # 2. Bleak gives you characteristics - you don't know what they are
            for char in service.characteristics:
                # char.uuid is also a full 128-bit UUID string
                print(f"  Characteristic UUID: {char.uuid}")

                # Try to read the value (returns bytes/bytearray)
                try:
                    raw_data = await client.read_gatt_char(char.uuid)
                    print(f"    Raw bytes: {raw_data.hex()}")

                    # Let bluetooth-sig identify and parse it
                    result = translator.parse_characteristic(
                        char.uuid, raw_data
                    )
                    print(f"    → Identified as: {result.info.name}")
                    print(f"    → Parsed value: {result.value}")

                except Exception as e:
                    print(f"    Could not read: {e}")


# Example output you'd see:
# Service UUID: 0000180f-0000-1000-8000-00805f9b34fb
#   → Identified as: Battery
#   Characteristic UUID: 00002a19-0000-1000-8000-00805f9b34fb
#     Raw bytes: 55
#     → Identified as: Battery Level
#     → Parsed value: 85
```

### UUID Format Conversion

BLE libraries output UUIDs in different formats, but bluetooth-sig handles them all:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery level

translator = BluetoothSIGTranslator()

found_uuid = translator.get_characteristic_uuid_by_name(
    CharacteristicName.BATTERY_LEVEL
)
# These all work - the library normalizes them internally
formats = [
    str(found_uuid),  # uuid found from Enum name
    "0x2A19",  # Hex prefix
    "00002a19-0000-1000-8000-00805f9b34fb",  # Full 128-bit (what bleak gives you)
    "00002A19-0000-1000-8000-00805F9B34FB",  # Uppercase variant
]

for uuid_format in formats:
    result = translator.parse_characteristic(
        str(uuid_format), SIMULATED_BATTERY_DATA
    )
    print(f"{uuid_format:45} → {result.info.name}")

# Output:
# 00002A19-0000-1000-8000-00805F9B34FB         → Battery Level
# 0x2A19                                       → Battery Level
# 00002a19-0000-1000-8000-00805f9b34fb         → Battery Level
# 00002A19-0000-1000-8000-00805F9B34FB         → Battery Level
```

For more basic usage examples, see the [Quick Start Guide](../tutorials/quickstart.md).

### Async Usage

If you are using an async BLE client (for example, bleak), you can await async wrappers without changing parsing logic:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = await translator.parse_characteristic_async("2A19", bytes([85]))
```

Prefer the existing examples for full context: see `examples/async_ble_integration.py`. The async classes are also documented in the Core API via mkdocstrings: `BluetoothSIGTranslator` and `AsyncParsingSession`.

## Real-World Usage Patterns

### Pattern 1: Fitness Tracker (Heart Rate + Battery)

Common in: Polar sensors, Fitbit devices, smartwatches

```python
from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()


async def monitor_fitness_device(address: str):
    async with BleakClient(address) as client:
        # Read battery level
        battery_uuid = "2A19"
        battery_data = await client.read_gatt_char(battery_uuid)
        battery = translator.parse_characteristic(battery_uuid, battery_data)
        print(f"Battery: {battery.value}%")

        # Subscribe to heart rate notifications
        hr_uuid = "2A37"

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
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()


async def read_environmental_sensors(devices: list[str]):
    """Read temp/humidity from multiple sensors"""
    for address in devices:
        async with BleakClient(address) as client:
            # Batch read multiple characteristics
            temp_uuid = "2A6E"
            humidity_uuid = "2A6F"
            battery_uuid = "2A19"

            temp_data = await client.read_gatt_char(temp_uuid)
            humidity_data = await client.read_gatt_char(humidity_uuid)
            battery_data = await client.read_gatt_char(battery_uuid)

            results = translator.parse_characteristics(
                {
                    temp_uuid: temp_data,
                    humidity_uuid: humidity_data,
                    battery_uuid: battery_data,
                }
            )

            print(f"Sensor {address}:")
            print(f"  Temp: {results[temp_uuid].value}°C")
            print(f"  Humidity: {results[humidity_uuid].value}%")
            print(f"  Battery: {results[battery_uuid].value}%")
```

### Pattern 3: Medical Device (Blood Pressure Monitor)

Common in: Omron blood pressure monitors, A&D medical devices, iHealth monitors

```python
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicData
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
            bpm = paired_data["2A35"]
            icp = paired_data["2A36"]

            print(f"Reading at {bpm.value.timestamp}:")
            print(f"  Final: {bpm.value.systolic}/{bpm.value.diastolic} mmHg")
            print(f"  Peak cuff: {icp.value.systolic} mmHg")
            completed_readings.append(paired_data)

        # Create pairing buffer that groups by timestamp
        buffer = DependencyPairingBuffer(
            translator=translator,
            required_uuids={
                "2A35",
                "2A36",
            },
            group_key=lambda data: data.value.timestamp
            if hasattr(data.value, "timestamp")
            else None,
            on_pair=on_complete_reading,
        )

        # Subscribe to both characteristics
        bpm_uuid = "2A35"
        icp_uuid = "2A36"

        await client.start_notify(
            bpm_uuid, lambda _, data: buffer.ingest(bpm_uuid, data)
        )
        await client.start_notify(
            icp_uuid, lambda _, data: buffer.ingest(icp_uuid, data)
        )

        await asyncio.sleep(60)  # Monitor for 1 minute

        print(f"\nCollected {len(completed_readings)} complete readings")
```

## Dependency-Aware Batch Parsing (Recommended)

When multiple characteristics are related (e.g., Blood Pressure Measurement `0x2A35` and Intermediate Cuff Pressure `0x2A36`), parse them together so the translator can handle them correctly.

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

# Raw values obtained from your BLE stack (notifications or reads)
bpm_uuid = "2A35"
icp_uuid = "2A36"

char_data = {
    bpm_uuid: blood_pressure_measurement_bytes,
    icp_uuid: intermediate_cuff_pressure_bytes,
}


# SKIP: Example showing SimpleBLE pattern
results = translator.parse_characteristics(char_data)

bpm_result = results[bpm_uuid]
icp_result = results[icp_uuid]

if bpm_result.parse_success and icp_result.parse_success:
    print(
        f"Blood Pressure: {bpm_result.value.systolic}/{bpm_result.value.diastolic} mmHg"
    )
    print(f"Peak Cuff Pressure: {icp_result.value.systolic} mmHg")
```

This batch API is the most user-friendly path: you provide UUIDs and raw bytes; the library parses each characteristic according to its specification.

## Strongly-Typed Raw Input Containers

If you prefer typed containers before calling the translator, use these types:

- `bluetooth_sig.types.io.RawCharacteristicRead` — holds a single read (`uuid`, `raw_data`, optional `descriptors`, optional `properties`).
- `bluetooth_sig.types.io.RawCharacteristicBatch` — a batch of reads.
- `bluetooth_sig.types.io.to_parse_inputs(batch)` — converts a batch to the exact `(char_data, descriptor_data)` shapes accepted by `parse_characteristics`.

Example:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.types.io import (
    RawCharacteristicBatch,
    RawCharacteristicRead,
    to_parse_inputs,
)

bpm_uuid = "2A35"
icp_uuid = "2A36"

batch = RawCharacteristicBatch(
    items=[
        RawCharacteristicRead(
            uuid=bpm_uuid, raw_data=blood_pressure_measurement_bytes
        ),
        RawCharacteristicRead(
            uuid=icp_uuid, raw_data=intermediate_cuff_pressure_bytes
        ),
    ]
)

char_data, descriptor_data = to_parse_inputs(batch)
results = BluetoothSIGTranslator().parse_characteristics(char_data)
```

## Converting Bleak/SimpleBLE Data

Example adapters for common connection managers are available in their respective files:

- `bleak_services_to_batch()` in `examples/connection_managers/bleak_utils.py`
- `simpleble_services_to_batch()` in `examples/connection_managers/simpleble.py`

These helpers use duck typing to avoid introducing BLE backend dependencies into the core library.

Usage sketch with Bleak:

```python
# SKIP: Example pattern - requires real BLE data
# Example showing the pattern - in practice you'd get these from actual BLE reads
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
bpm_uuid = "2A35"
icp_uuid = "2A36"

# Your BLE library gives you raw bytes from device
char_data = {
    bpm_uuid: blood_pressure_measurement_bytes,
    icp_uuid: intermediate_cuff_pressure_bytes,
}

results = translator.parse_characteristics(char_data)
for uuid, result in results.items():
    if result.parse_success:
        print(f"{result.info.name}: {result.value}")
```

The same pattern works with SimpleBLE:

```python
# SKIP: Example pattern - requires SimpleBLE data
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Get raw bytes from SimpleBLE reads
char_data = {
    "2A19": battery_bytes,  # From SimpleBLE read
    "2A6E": temp_bytes,  # From SimpleBLE read
}

results = translator.parse_characteristics(char_data)
```

These helpers align with what Bleak and SimpleBLE typically expose: service collections with characteristic entries (`uuid`, optional `properties`, optional `descriptors`). They avoid making network calls; provide `values_by_uuid` from your reads/notifications. Example adapters live under `examples/connection_managers/` and may need updates to match your backend versions—copy and tweak as needed.

For a step-by-step porting overview (before/after), see the [Migration Guide](migration.md).

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
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual device
# ============================================
SIMULATED_DEVICE_ADDRESS = (
    "AA:BB:CC:DD:EE:FF"  # Example MAC address - use your actual device address
)
# Advertisement data encoding "Test Device" as local name
SIMULATED_ADV_DATA = bytes(
    [
        0x0C,
        0x09,
        0x54,
        0x65,
        0x73,
        0x74,
        0x20,
        0x44,
        0x65,
        0x76,
        0x69,
        0x63,
        0x65,  # Local Name
    ]
)


async def main():
    # Create translator and device
    translator = BluetoothSIGTranslator()
    device = Device(SIMULATED_DEVICE_ADDRESS, translator)

    # Parse advertisement data
    device.parse_advertiser_data(SIMULATED_ADV_DATA)
    print(f"Device name: {device.name}")

    # Discover services (real workflow with connection manager)
    await device.discover_services()

    # SKIP: Example uses Device abstraction
    # Read characteristic data using high-level enum
    battery_uuid = "2A19"
    battery_level = await device.read(battery_uuid)
    print(f"Battery level: {battery_level.value}%")

    # Check encryption requirements
    print(f"Requires encryption: {device.encryption.requires_encryption}")
    print(
        f"Requires authentication: {device.encryption.requires_authentication}"
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

### Device with BLE Connection Library

The Device class integrates with any BLE connection library:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.types.gatt_enums import CharacteristicName


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
        print(
            f"Service {service_uuid}: {len(service_data.characteristics)} characteristics"
        )

    return device
```

### Device Data Structures

The Device class uses several data structures:

- `DeviceService`: Groups a service with its parsed characteristics
- `DeviceEncryption`: Tracks encryption and authentication requirements
- `DeviceAdvertiserData`: Parsed advertisement data including manufacturer info, service UUIDs, etc.

All data structures follow the Bluetooth SIG specifications and provide type-safe access to device information.

## Next Steps

- [Quick Start Guide](../tutorials/quickstart.md) - Basic getting started
- [BLE Integration Guide](ble-integration.md) - Connect with bleak, simplepyble, etc.
- [Supported Characteristics](../reference/characteristics.md) - Complete list of supported GATT characteristics
- [API Reference](../api/index.md) - Detailed API documentation
- [Testing Guide](testing.md) - How to test your BLE integration
