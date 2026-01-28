# BLE Integration Guide

Learn how to integrate bluetooth-sig with your preferred BLE connection library.

## Philosophy

The bluetooth-sig library follows a clean separation of concerns:

- **BLE Library** → Device connection, I/O operations, provides UUIDs
- **bluetooth-sig** → Automatic UUID identification, standards interpretation, data parsing

**You don't need to know what the UUIDs mean!** Your BLE library gives you UUIDs, and bluetooth-sig automatically identifies them and parses the data correctly.

This design lets you choose the best BLE library for your platform while using bluetooth-sig for consistent data parsing.

## Choose Your Approach

This guide covers all three parsing approaches. For help deciding which to use, see [Choosing the Right API](../explanation/api-overview.md).

## Device Abstraction (Recommended)

The `Device` class provides the highest-level API for BLE integration, allowing for swapping out BLE backends without effecting your application code. It handles connection management, service discovery, dependency resolution, and type-safe reads/writes:

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    TemperatureCharacteristic,
)

# Connection manager from examples - use for your BLE backend
from examples.connection_managers.bleak_retry import (
    BleakRetryConnectionManager,
)


async def use_device(address: str):
    """Recommended: Use Device abstraction for apps."""
    translator = BluetoothSIGTranslator()
    connection_manager = BleakRetryConnectionManager(address)
    device = Device(connection_manager, translator)

    await device.connect()

    try:
        # Type-safe reads - pass characteristic class
        battery: int | None = await device.read(BatteryLevelCharacteristic)
        print(f"Battery: {battery}%")

        temp: float | None = await device.read(TemperatureCharacteristic)
        print(f"Temperature: {temp}°C")

        # Device handles dependency resolution automatically
        # For example, if reading a measurement that depends on a feature
        # characteristic, Device reads the feature first and caches it.

    finally:
        await device.disconnect()


asyncio.run(use_device("AA:BB:CC:DD:EE:FF"))
```

**Benefits of Device abstraction:**

- **Automatic dependency resolution**: Measurement characteristics that depend on feature characteristics are handled automatically
- **Caching**: Feature characteristics are cached after first read
- **Type-safe reads/writes**: Pass characteristic class for full IDE inference
- **Connection management**: Integrates with connection manager protocol

## Type-Safe Integration (Direct Classes)

When you know the device, services and characteristics, you can use classes directly for full IDE type inference:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)


async def read_known_device(address: str):
    """Read from a device with known characteristics."""
    battery = BatteryLevelCharacteristic()
    temp = TemperatureCharacteristic()
    humidity = HumidityCharacteristic()

    async with BleakClient(address) as client:
        # Use characteristic's uuid property - no hardcoded strings
        battery_data = await client.read_gatt_char(str(battery.uuid))
        level = battery.parse_value(battery_data)  # IDE knows: int
        print(f"Battery: {level}%")

        temp_data = await client.read_gatt_char(str(temp.uuid))
        temp_value = temp.parse_value(temp_data)  # IDE knows: float
        print(f"Temperature: {temp_value}°C")

        humidity_data = await client.read_gatt_char(str(humidity.uuid))
        humidity_value = humidity.parse_value(
            humidity_data
        )  # IDE knows: float
        print(f"Humidity: {humidity_value}%")


asyncio.run(read_known_device("AA:BB:CC:DD:EE:FF"))
```

## Dynamic Integration (Device Scanning)

For scanning unknown devices, use the Translator with UUID strings:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator


async def scan_unknown_device(address: str):
    """Discover and parse characteristics from an unknown device."""
    translator = BluetoothSIGTranslator()

    async with BleakClient(address) as client:
        for service in client.services:
            for char in service.characteristics:
                # UUID comes from device discovery - we don't know what it is
                uuid_str = str(char.uuid)

                if translator.supports(uuid_str):
                    try:
                        raw_data = await client.read_gatt_char(char.uuid)
                        value = translator.parse_characteristic(
                            uuid_str, raw_data
                        )
                        # Get info separately for name/unit
                        info = translator.get_characteristic_info_by_uuid(
                            uuid_str
                        )
                        print(f"Found: {info.name} = {value}")
                    except Exception:
                        pass  # Characteristic may not be readable


asyncio.run(scan_unknown_device("AA:BB:CC:DD:EE:FF"))
```

## Integration with bleak

[bleak](https://github.com/hbldh/bleak) is a cross-platform async BLE library (recommended).

### bleak Installation

```bash
pip install bluetooth-sig bleak
```

### Notifications with Type-Safe Parsing

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)


async def monitor_heart_rate(address: str):
    heart_rate = HeartRateMeasurementCharacteristic()

    def on_notification(sender, data: bytearray):
        hr_data = heart_rate.parse_value(data)  # IDE knows: HeartRateData
        print(f"Heart Rate: {hr_data.heart_rate} bpm")
        print(f"Sensor contact: {hr_data.sensor_contact}")

    async with BleakClient(address) as client:
        await client.start_notify(str(heart_rate.uuid), on_notification)
        await asyncio.sleep(30)  # Monitor for 30 seconds
        await client.stop_notify(str(heart_rate.uuid))


asyncio.run(monitor_heart_rate("AA:BB:CC:DD:EE:FF"))
```

### Reading Multiple Characteristics (Type-Safe)

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)


async def read_environmental_sensors(address: str):
    """Read multiple characteristics with full type safety."""
    characteristics = [
        BatteryLevelCharacteristic(),
        TemperatureCharacteristic(),
        HumidityCharacteristic(),
    ]

    async with BleakClient(address) as client:
        for char in characteristics:
            try:
                raw_data = await client.read_gatt_char(str(char.uuid))
                value = char.parse_value(raw_data)
                print(f"{char.name}: {value} {char.info.unit or ''}")
            except Exception as e:
                print(f"{char.name}: Failed to read - {e}")


asyncio.run(read_environmental_sensors("AA:BB:CC:DD:EE:FF"))
```

### Reading Multiple Characteristics (Dynamic)

When scanning unknown devices, use the Translator to identify and parse discovered characteristics:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery
SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])  # Simulates 24.04°C
SIMULATED_HUMIDITY_DATA = bytearray([0x3A, 0x13])  # Simulates 49.22%


async def read_sensor_data(address: str):
    """Read multiple characteristics using dynamic discovery."""
    translator = BluetoothSIGTranslator()

    # Simulated data from BLE reads - in reality from client.read_gatt_char()
    characteristics = {
        "Battery": ("2A19", SIMULATED_BATTERY_DATA),
        "Temperature": ("2A6E", SIMULATED_TEMP_DATA),
        "Humidity": ("2A6F", SIMULATED_HUMIDITY_DATA),
    }

    # Parse each characteristic - translator auto-identifies them
    for name, (uuid, raw_data) in characteristics.items():
        value = translator.parse_characteristic(uuid, raw_data)
        info = translator.get_characteristic_info_by_uuid(uuid)
        print(f"{name}: {value}{info.unit if info else ''}")


asyncio.run(read_sensor_data("AA:BB:CC:DD:EE:FF"))
```

## Integration with bleak-retry-connector

[bleak-retry-connector](https://github.com/Bluetooth-Devices/bleak-retry-connector)
adds robust retry logic (recommended).

### bleak-retry-connector Installation

```bash
pip install bluetooth-sig bleak-retry-connector
```

### Example (bleak-retry-connector)

```python
import asyncio

from bleak_retry_connector import establish_connection

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic


async def read_with_retry(address: str):
    battery = BatteryLevelCharacteristic()

    # Robust connection with automatic retries
    client = await establish_connection(address)

    try:
        raw_data = await client.read_gatt_char(str(battery.uuid))
        level = battery.parse_value(raw_data)  # IDE knows: int
        print(f"Battery: {level}%")
    finally:
        await client.disconnect()


asyncio.run(read_with_retry("AA:BB:CC:DD:EE:FF"))
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
# SKIP: Requires real Bluetooth hardware
from simplepyble import Adapter

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic


def main():
    battery = BatteryLevelCharacteristic()

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
        # Read battery level using characteristic's UUID
        service_uuid = "180F"  # Battery Service
        raw_data = peripheral.read(service_uuid, str(battery.uuid))
        level = battery.parse_value(bytearray(raw_data))  # IDE knows: int
        print(f"Battery: {level}%")
    finally:
        peripheral.disconnect()


if __name__ == "__main__":
    main()
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
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    TemperatureCharacteristic,
)

# Create characteristic instances once
battery = BatteryLevelCharacteristic()
temp = TemperatureCharacteristic()

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])
SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])

# ✅ Good - type-safe parsing with known characteristics
battery_level = battery.parse_value(SIMULATED_BATTERY_DATA)  # int
temp_value = temp.parse_value(SIMULATED_TEMP_DATA)  # float

print(f"Battery: {battery_level}%")
print(f"Temperature: {temp_value}°C")
```

## Complete Example

Here's a complete example using type-safe characteristic classes:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError


class SensorReader:
    """Read and parse BLE sensor data with type safety."""

    def __init__(self, address: str):
        self.address = address
        self.battery = BatteryLevelCharacteristic()
        self.temperature = TemperatureCharacteristic()
        self.humidity = HumidityCharacteristic()

    async def read_battery(self) -> int:
        """Read battery level."""
        async with BleakClient(self.address) as client:
            raw_data = await client.read_gatt_char(str(self.battery.uuid))
            return self.battery.parse_value(raw_data)  # Returns int

    async def read_temperature(self) -> float:
        """Read temperature in °C."""
        async with BleakClient(self.address) as client:
            raw_data = await client.read_gatt_char(str(self.temperature.uuid))
            return self.temperature.parse_value(raw_data)  # Returns float

    async def read_all(self) -> dict:
        """Read all sensor data."""
        results = {}
        characteristics = [
            ("battery", self.battery),
            ("temperature", self.temperature),
            ("humidity", self.humidity),
        ]

        async with BleakClient(self.address) as client:
            for name, char in characteristics:
                try:
                    raw_data = await asyncio.wait_for(
                        client.read_gatt_char(str(char.uuid)), timeout=5.0
                    )
                    results[name] = char.parse_value(raw_data)
                except CharacteristicParseError as e:
                    print(f"Parse error for {name}: {e}")
                except Exception as e:
                    print(f"BLE error for {name}: {e}")

        return results


async def main():
    reader = SensorReader("AA:BB:CC:DD:EE:FF")

    # Read battery - IDE knows this returns int
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
- [API Reference](../api/index.md) - Full API documentation
- [Examples](https://github.com/ronanb96/bluetooth-sig-python/tree/main/examples) - More examples and patterns
