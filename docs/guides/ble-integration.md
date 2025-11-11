# BLE Integration Guide

Learn how to integrate bluetooth-sig with your preferred BLE connection
library.

## Philosophy

The bluetooth-sig library follows a clean separation of concerns:

- **BLE Library** → Device connection, I/O operations
- **bluetooth-sig** → Standards interpretation, data parsing

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
from bleak import BleakClient, BleakScanner
from bluetooth_sig import BluetoothSIGTranslator

async def main():
    translator = BluetoothSIGTranslator()

    # Scan for devices
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found: {device.name} ({device.address})")

    # Connect to device
    address = "AA:BB:CC:DD:EE:FF"
    async with BleakClient(address) as client:
        # Read battery level
        raw_data = await client.read_gatt_char("2A19")

        # Parse with bluetooth-sig
    result = translator.parse_characteristic("2A19", raw_data)
    print(
        f"Battery: {result.value}%"
    )

asyncio.run(main())
```

### Reading Multiple Characteristics

```python
async def read_sensor_data(address: str):
    translator = BluetoothSIGTranslator()

    async with BleakClient(address) as client:
        # Define characteristics to read
        characteristics = {
            "Battery": "2A19",
            "Temperature": "2A6E",
            "Humidity": "2A6F",
        }

        # Read and parse
        for name, uuid in characteristics.items():
            try:
                raw_data = await client.read_gatt_char(uuid)
                result = translator.parse_characteristic(uuid, raw_data)
                print(f"{name}: {result.value}")
            except Exception as e:
                print(f"Failed to read {name}: {e}")
```

### Handling Notifications

```python
def notification_handler(sender, data):
    """Handle BLE notifications."""
    translator = BluetoothSIGTranslator()

    # Parse the notification data
    uuid = str(sender.uuid)
    result = translator.parse_characteristic(uuid, data)
    print(f"Notification from {uuid}: {result.value}")

async def subscribe_to_notifications(address: str):
    async with BleakClient(address) as client:
        # Subscribe to heart rate notifications
        await client.start_notify("2A37", notification_handler)

        # Keep listening
        await asyncio.sleep(30)

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
import asyncio
from bleak_retry_connector import establish_connection
from bluetooth_sig import BluetoothSIGTranslator

async def read_with_retry(address: str):
    translator = BluetoothSIGTranslator()

    # Establish connection with automatic retries
    client = await establish_connection(
        BleakClient,
        address,
        name="Sensor Device",
        max_attempts=3
    )

    try:
        # Read battery level
        raw_data = await client.read_gatt_char("2A19")
        result = translator.parse_characteristic("2A19", raw_data)
    print(f"Battery: {result.value}%")
    finally:
        await client.disconnect()
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
            (s for s in services if s.uuid() == "180F"),
            None
        )

        if battery_service:
            # Find battery level characteristic
            battery_char = next(
                (c for c in battery_service.characteristics()
                 if c.uuid() == "2A19"),
                None
            )

            if battery_char:
                # Read and parse
                raw_data = peripheral.read(
                    battery_service.uuid(),
                    battery_char.uuid()
                )
                result = translator.parse_characteristic(
                    "2A19",
                    bytearray(raw_data)
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
raw_data = await asyncio.wait_for(
    client.read_gatt_char(uuid),
    timeout=10.0
)

# ❌ Bad - no timeout (could hang forever)
raw_data = await client.read_gatt_char(uuid)
```

### 4. Reuse Translator

Create one translator instance and reuse it:

```python
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
            result = self.translator.parse_characteristic(
                "2A19",
                raw_data
            )
            return result.value

    async def read_temperature(self) -> float:
        """Read temperature in °C."""
        async with BleakClient(self.address) as client:
            raw_data = await client.read_gatt_char("2A6E")
            result = self.translator.parse_characteristic(
                "2A6E",
                raw_data
            )
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
                        client.read_gatt_char(uuid),
                        timeout=5.0
                    )
                    result = self.translator.parse_characteristic(
                        uuid,
                        raw_data
                    )
                    results[name] = result.value
                except BluetoothSIGError as e:
                    print(f"Parse error for {name}: {e}")
                except Exception as e:
                    print(f"BLE error for {name}: {e}")

        return results

async def main():
    reader = SensorReader("AA:BB:CC:DD:EE:FF")

    # Read battery
    battery = await reader.read_battery()
    print(f"Battery: {battery}%")

    # Read all sensors
    data = await reader.read_all()
    for name, value in data.items():
        print(
            f"{name}: {value}"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## See Also

- [Quick Start](../quickstart.md) - Basic usage
- [API Reference](../api/core.md) - Full API documentation
- [Examples](https://github.com/ronanb96/bluetooth-sig-python/tree/main/examples)
  - More examples
  - Additional resources
  - Community support
  - More examples
