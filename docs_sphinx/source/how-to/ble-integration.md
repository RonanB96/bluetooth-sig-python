# BLE Integration Guide

Learn how to integrate bluetooth-sig with your preferred BLE connection
library.

## Philosophy

The bluetooth-sig library follows a clean separation of concerns:

- **BLE Library** → Device connection, I/O operations, provides UUIDs
- **bluetooth-sig** → Automatic UUID identification, standards interpretation, data parsing

**You don't need to know what the UUIDs mean!** Your BLE library gives you UUIDs, and bluetooth-sig automatically identifies them and parses the data correctly.

This design lets you choose the best BLE library for your platform while using
bluetooth-sig for consistent data parsing.

## Integration with bleak

[bleak](https://github.com/hbldh/bleak) is a cross-platform async BLE library (recommended).

### bleak Installation

```bash
pip install bluetooth-sig bleak
```

### Basic Example

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery level


async def main():
    translator = BluetoothSIGTranslator()

    # Example: Your BLE library gives you UUIDs - you don't need to know what they mean!
    battery_uuid = "2A19"  # From your BLE library

    # bluetooth-sig automatically identifies it and parses correctly
    result = translator.parse_characteristic(
        battery_uuid, SIMULATED_BATTERY_DATA
    )
    print(f"Discovered: {result.info.name}")  # "Battery Level"
    print(f"Battery: {result.value}%")  # 85%

    # Alternative: If you know the characteristic, convert enum to UUID first
    from bluetooth_sig.types.gatt_enums import CharacteristicName

    battery_uuid = translator.get_characteristic_uuid_by_name(
        CharacteristicName.BATTERY_LEVEL
    )
    if battery_uuid:
        result2 = translator.parse_characteristic(
            str(battery_uuid), SIMULATED_BATTERY_DATA
        )
        print(f"Using enum: {result2.info.name} = {result2.value}%")


asyncio.run(main())
```

### Reading Multiple Characteristics

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery
SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])  # Simulates 24.04°C
SIMULATED_HUMIDITY_DATA = bytearray([0x3A, 0x13])  # Simulates 49.22%


async def read_sensor_data():
    translator = BluetoothSIGTranslator()

    # Example data from BLE reads - use UUIDs from your BLE library
    characteristics = {
        "Battery": ("2A19", SIMULATED_BATTERY_DATA),
        "Temperature": ("2A6E", SIMULATED_TEMP_DATA),
        "Humidity": ("2A6F", SIMULATED_HUMIDITY_DATA),
    }

    # Parse each characteristic
    for name, (uuid, raw_data) in characteristics.items():
        result = translator.parse_characteristic(uuid, raw_data)
        if result.parse_success:
            print(f"{name}: {result.value}{result.info.unit or ''}")


asyncio.run(read_sensor_data())
```

### Handling Notifications

```python
# SKIP: Notification handler pattern - not standalone executable
import asyncio
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# SKIP: Callback function pattern
def notification_handler(sender, data):
    """Handle BLE notifications."""
    # Parse the notification data
    uuid = "2A37"  # Heart rate measurement
    result = translator.parse_characteristic(uuid, data)
    if result.parse_success:
        print(f"Heart Rate: {result.value.heart_rate} bpm")

# SKIP: Example wrapper
# SKIP: Example function
    async def example():
    # Simulate notification
    notification_handler(None, bytearray([0x00, 0x55]))

asyncio.run(example())

        # Unsubscribe
        await client.stop_notify("2A37")


```

## Integration with bleak-retry-connector

[bleak-retry-connector](https://github.com/Bluetooth-Devices/bleak-retry-connector)
adds robust retry logic (recommended for production).

### bleak-retry-connector Installation

```bash
pip install bluetooth-sig bleak-retry-connector
```

### Example (bleak-retry-connector)

```python
# SKIP: Example pattern only
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def read_with_retry():
    translator = BluetoothSIGTranslator()

    # Example: reading battery level
    raw_data = bytearray([85])
    result = translator.parse_characteristic("2A19", raw_data)
    print(f"Battery: {result.value}%")


asyncio.run(read_with_retry())
```

## Integration with simplepyble

[simplepyble](https://github.com/OpenBluetoothToolbox/SimpleBLE) is a cross-platform
sync BLE library.

### simplepyble Installation

```bash
pip install bluetooth-sig simplepyble
```

### Example (simplepyble)

```python
from simplepyble import Adapter, Peripheral

from bluetooth_sig import BluetoothSIGTranslator


def main():
    translator = BluetoothSIGTranslator()

    # Get adapter
    adapters = Adapter.get_adapters()
    if not adapters:
        print("No adapters found")
        return

    adapter = adapters[0]

    # Scan for devices
    adapter.scan_for(5000)  # 5 seconds
    peripherals = adapter.scan_get_results()

    if not peripherals:
        print("No devices found")
        return

    # Connect to first device
    peripheral = peripherals[0]
    peripheral.connect()

    try:
        # Find battery service
        services = peripheral.services()
        battery_service = next(
            (s for s in services if s.uuid() == "180F"), None
        )

        if battery_service:
            # Find battery level characteristic
            battery_char = next(
                (
                    c
                    for c in battery_service.characteristics()
                    if c.uuid() == "2A19"
                ),
                None,
            )

            if battery_char:
                # Read and parse
                raw_data = peripheral.read(
                    battery_service.uuid(), battery_char.uuid()
                )
                result = translator.parse_characteristic(
                    "2A19", bytearray(raw_data)
                )
                print(f"Battery: {result.value}%")
    finally:
        peripheral.disconnect()
```

## Best Practices

### 1. Error Handling

Always handle exceptions from both BLE operations and parsing:

```python
from bluetooth_sig.gatt.exceptions import (
    InsufficientDataError,
    ValueRangeError,
)

try:
    # BLE operation
    raw_data = await client.read_gatt_char(uuid)

    # Parse
    result = translator.parse_characteristic(uuid, raw_data)

except BleakError as e:
    print(f"BLE error: {e}")
except InsufficientDataError as e:
    print(f"Data too short: {e}")
except ValueRangeError as e:
    print(f"Invalid value: {e}")
```

### 2. Connection Management

Use context managers for automatic cleanup:

```python
# ✅ Good - automatic cleanup
async with BleakClient(address) as client:
    result = translator.parse_characteristic(uuid, data)

# ❌ Bad - manual cleanup required
client = BleakClient(address)
await client.connect()
# ...
await client.disconnect()
```

### 3. Timeouts

Always specify timeouts:

```python
# ✅ Good - with timeout
raw_data = await asyncio.wait_for(client.read_gatt_char(uuid), timeout=10.0)

# ❌ Bad - no timeout (could hang forever)
raw_data = await client.read_gatt_char(uuid)
```

### 4. Reuse Translator

Create one translator instance and reuse it:

```python
from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
sensor_data = {"2A19": bytearray([85]), "2A6E": bytearray([0x64, 0x09])}

# ✅ Good - reuse translator
translator = BluetoothSIGTranslator()
for uuid, data in sensor_data.items():
    result = translator.parse_characteristic(uuid, data)

# ❌ Bad - creating multiple instances
for uuid, data in sensor_data.items():
    translator = BluetoothSIGTranslator()  # Wasteful
    result = translator.parse_characteristic(uuid, data)
```

## Complete Example

Here's a complete production-ready example:

```python
# SKIP: Requires actual BLE device connection
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import BluetoothSIGError


class SensorReader:
    """Read and parse BLE sensor data."""

    def __init__(self, address: str):
        self.address = address
        self.translator = BluetoothSIGTranslator()

    async def read_battery(self) -> int:
        """Read battery level."""
        async with BleakClient(self.address) as client:
            raw_data = await client.read_gatt_char("2A19")
            result = self.translator.parse_characteristic("2A19", raw_data)
            return result.value

    async def read_temperature(self) -> float:
        """Read temperature in °C."""
        async with BleakClient(self.address) as client:
            raw_data = await client.read_gatt_char("2A6E")
            result = self.translator.parse_characteristic("2A6E", raw_data)
            return result.value

    async def read_all(self) -> dict:
        """Read all sensor data."""
        results = {}

        async with BleakClient(self.address) as client:
            sensors = {
                "battery": "2A19",
                "temperature": "2A6E",
                "humidity": "2A6F",
            }

            for name, uuid in sensors.items():
                try:
                    raw_data = await asyncio.wait_for(
                        client.read_gatt_char(uuid), timeout=5.0
                    )
                    result = self.translator.parse_characteristic(
                        uuid, raw_data
                    )
                    results[name] = result.value
                except BluetoothSIGError as e:
                    print(f"Parse error for {name}: {e}")
                except Exception as e:
                    print(f"BLE error for {name}: {e}")

        return results


# ============================================
# SIMULATED DATA - Replace with actual device
# ============================================
SIMULATED_DEVICE_ADDRESS = "AA:BB:CC:DD:EE:FF"  # Example MAC address


async def main():
    reader = SensorReader(SIMULATED_DEVICE_ADDRESS)

    # Read battery
    battery = await reader.read_battery()
    print(f"Battery: {battery}%")

    # Read all sensors
    data = await reader.read_all()
    for name, value in data.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
```

## See Also

- [Quick Start](../tutorials/quickstart.md) - Basic usage
- [API Reference](../reference/bluetooth_sig/index.md) - Full API documentation
- [Examples](https://github.com/ronanb96/bluetooth-sig-python/tree/main/examples)
  - More examples
  - Additional resources
  - Community support
  - More examples
