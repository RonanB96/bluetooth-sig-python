# Async Usage Guide

Learn how to use the async APIs for BLE device communication and data parsing.

## When to Use Async

Use the async API when:

- Working with async BLE libraries (bleak, etc.)
- Parsing large batches of characteristics
- Building async applications (FastAPI, asyncio-based)
- Need concurrent parsing operations

The async API maintains full backward compatibility—all sync methods remain available.

## Device Class (Recommended for Real Devices)

For applications with real BLE devices, the `Device` class provides the highest-level async API with automatic connection management, dependency resolution, and caching:

```python
# SKIP: Requires actual BLE device connection
import asyncio

from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
    TemperatureCharacteristic,
)

# Connection manager for your BLE backend
from examples.connection_managers.bleak_retry import (
    BleakRetryClientManager,
)


async def production_example(address: str):
    """Recommended pattern for real device integration."""
    translator = BluetoothSIGTranslator()
    connection_manager = BleakRetryClientManager(address)
    device = Device(connection_manager, translator)

    await device.connect()

    try:
        # Type-safe reads - IDE knows the return types
        battery: int | None = await device.read(BatteryLevelCharacteristic)
        print(f"Battery: {battery}%")

        temp: float | None = await device.read(TemperatureCharacteristic)
        print(f"Temperature: {temp}°C")

        # Notifications with type-safe callback
        def on_heart_rate(data: bytes):
            hr = HeartRateMeasurementCharacteristic()
            hr_data = hr.parse_value(data)
            print(f"Heart Rate: {hr_data.heart_rate} bpm")

        await device.start_notify(
            HeartRateMeasurementCharacteristic, on_heart_rate
        )
        await asyncio.sleep(30)  # Monitor for 30 seconds
        await device.stop_notify(HeartRateMeasurementCharacteristic)

    finally:
        await device.disconnect()


asyncio.run(production_example("AA:BB:CC:DD:EE:FF"))
```

**Device class benefits:**

- **Automatic dependency resolution**: Measurement characteristics that depend on feature characteristics are resolved automatically
- **Caching**: Feature characteristics are cached after first read
- **Type-safe reads/writes**: Pass characteristic class for full IDE inference
- **Connection management**: Integrates with connection manager protocol
- **Notification support**: Type-safe notification subscriptions

For more on Device usage, see [BLE Integration Guide](ble-integration.md).

## Translator Async Methods

For parsing raw bytes without device connection (e.g., testing, simulated data), use the Translator's async methods:

| Method | Description | Type-Safe Overload |
|--------|-------------|-------------------|
| `parse_characteristic_async()` | Parse raw bytes to typed value | ✅ With characteristic class |
| `parse_characteristics_async()` | Batch parse multiple UUIDs | ❌ Returns `dict[str, Any]` |
| `encode_characteristic_async()` | Encode value to bytes | ✅ With characteristic class |

## parse_characteristic_async

Parse a single characteristic asynchronously.

### Type-Safe Usage (Recommended)

Pass a characteristic **class** for full type inference:

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)

SIMULATED_BATTERY_DATA = bytearray([75])
SIMULATED_HR_DATA = bytearray([0x00, 0x48])  # 72 bpm


async def main():
    translator = BluetoothSIGTranslator()

    # Type-safe: IDE knows level is int
    level: int = await translator.parse_characteristic_async(
        BatteryLevelCharacteristic, SIMULATED_BATTERY_DATA
    )
    print(f"Battery: {level}%")  # Battery: 75%

    # Type-safe: IDE knows hr_data is HeartRateMeasurement
    hr_data = await translator.parse_characteristic_async(
        HeartRateMeasurementCharacteristic, SIMULATED_HR_DATA
    )
    print(f"Heart Rate: {hr_data.heart_rate} bpm")  # Heart Rate: 72 bpm


asyncio.run(main())
```

### Dynamic Usage (Discovery Scenarios)

Pass a UUID string when you don't know the characteristic at compile time:

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def parse_discovered_characteristic(uuid: str, data: bytes):
    """Parse a characteristic discovered at runtime."""
    translator = BluetoothSIGTranslator()

    # Dynamic: returns Any (no type inference)
    value = await translator.parse_characteristic_async(uuid, data)

    # Get metadata separately if needed
    info = translator.get_characteristic_info_by_uuid(uuid)
    if info:
        print(f"{info.name}: {value}")
    return value


# Example with simulated data
asyncio.run(parse_discovered_characteristic("2A19", bytearray([85])))
```

## parse_characteristics_async

Batch parse multiple characteristics in one async call. Handles dependency ordering automatically.

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)

# Simulated sensor data
BATTERY_DATA = bytearray([75])
TEMP_DATA = bytearray([0x64, 0x09])  # 24.04°C
HUMIDITY_DATA = bytearray([0x3A, 0x13])  # 49.22%


async def batch_parse_sensors():
    translator = BluetoothSIGTranslator()

    # Use characteristic classes for UUID references
    battery = BatteryLevelCharacteristic()
    temp = TemperatureCharacteristic()
    humidity = HumidityCharacteristic()

    # Build data dict with UUIDs as keys
    char_data = {
        str(battery.uuid): BATTERY_DATA,
        str(temp.uuid): TEMP_DATA,
        str(humidity.uuid): HUMIDITY_DATA,
    }

    # Async batch parsing - returns dict[str, Any]
    results = await translator.parse_characteristics_async(char_data)

    # Access parsed values by UUID
    print(f"Battery: {results[str(battery.uuid)]}%")
    print(f"Temperature: {results[str(temp.uuid)]}°C")
    print(f"Humidity: {results[str(humidity.uuid)]}%")


asyncio.run(batch_parse_sensors())
```

## encode_characteristic_async

Encode a value for writing to a characteristic asynchronously.

### Type-Safe Usage

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import AlertLevelCharacteristic
from bluetooth_sig.gatt.characteristics.alert_level import AlertLevel


async def encode_alert():
    translator = BluetoothSIGTranslator()

    # Type-safe: value type is checked against characteristic
    encoded: bytes = await translator.encode_characteristic_async(
        AlertLevelCharacteristic, AlertLevel.HIGH_ALERT
    )
    print(f"Encoded bytes: {encoded.hex()}")  # Encoded bytes: 02
    return encoded


asyncio.run(encode_alert())
```

### Dynamic Usage

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def encode_by_uuid(uuid: str, value):
    """Encode using UUID string (no type checking)."""
    translator = BluetoothSIGTranslator()

    encoded = await translator.encode_characteristic_async(uuid, value)
    return encoded


# Example: encode alert level by UUID
asyncio.run(encode_by_uuid("2A06", 2))  # High alert
```

## Integration with Bleak

Example Use async methods with [Bleak](https://github.com/hbldh/bleak) for BLE communication:

```python
# SKIP: Requires actual BLE device connection
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    TemperatureCharacteristic,
)


async def read_and_parse(address: str):
    translator = BluetoothSIGTranslator()
    battery = BatteryLevelCharacteristic()
    temp = TemperatureCharacteristic()

    async with BleakClient(address) as client:
        # Read from device
        battery_data = await client.read_gatt_char(str(battery.uuid))
        temp_data = await client.read_gatt_char(str(temp.uuid))

        # Parse with type-safe async methods
        level: int = await translator.parse_characteristic_async(
            BatteryLevelCharacteristic, battery_data
        )
        temp_value: float = await translator.parse_characteristic_async(
            TemperatureCharacteristic, temp_data
        )

        print(f"Battery: {level}%")
        print(f"Temperature: {temp_value}°C")


asyncio.run(read_and_parse("AA:BB:CC:DD:EE:FF"))
```

## Batch Parse with Bleak

Read and parse multiple characteristics efficiently:

```python
# SKIP: Requires actual BLE device connection
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HumidityCharacteristic,
    TemperatureCharacteristic,
)


async def batch_read_and_parse(address: str):
    translator = BluetoothSIGTranslator()

    # Define characteristics to read
    battery = BatteryLevelCharacteristic()
    temp = TemperatureCharacteristic()
    humidity = HumidityCharacteristic()

    async with BleakClient(address) as client:
        # Read all characteristics
        char_data = {
            str(battery.uuid): await client.read_gatt_char(str(battery.uuid)),
            str(temp.uuid): await client.read_gatt_char(str(temp.uuid)),
            str(humidity.uuid): await client.read_gatt_char(
                str(humidity.uuid)
            ),
        }

        # Batch parse asynchronously
        results = await translator.parse_characteristics_async(char_data)

        # Results are parsed values directly
        print(f"Battery: {results[str(battery.uuid)]}%")
        print(f"Temperature: {results[str(temp.uuid)]}°C")
        print(f"Humidity: {results[str(humidity.uuid)]}%")


asyncio.run(batch_read_and_parse("AA:BB:CC:DD:EE:FF"))
```

## Write with encode_characteristic_async

Encode and write values to a device:

```python
# SKIP: Requires actual BLE device connection
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import AlertLevelCharacteristic
from bluetooth_sig.gatt.characteristics.alert_level import AlertLevel


async def write_alert(address: str, level: AlertLevel):
    translator = BluetoothSIGTranslator()
    alert = AlertLevelCharacteristic()

    async with BleakClient(address) as client:
        # Encode with type-safety
        encoded = await translator.encode_characteristic_async(
            AlertLevelCharacteristic, level
        )

        # Write to device
        await client.write_gatt_char(str(alert.uuid), encoded)
        print(f"Wrote alert level: {level.name}")


asyncio.run(write_alert("AA:BB:CC:DD:EE:FF", AlertLevel.HIGH_ALERT))
```

## Performance Notes

The async methods are **async-compatible wrappers** around synchronous parsing:

- Parsing is CPU-bound and executes synchronously (fast)
- Async wrappers allow natural use in async workflows
- No performance penalty - parsing completes immediately
- Benefits come from combining with async I/O (BLE reads/writes)

## AsyncParsingSession

For maintaining parsing context across multiple async operations, use `AsyncParsingSession`:

```python
import asyncio

from bluetooth_sig import AsyncParsingSession, BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)

SIMULATED_BATTERY_DATA = bytearray([85])
SIMULATED_HR_DATA = bytearray([0x00, 0x48])


async def parsing_session_example():
    translator = BluetoothSIGTranslator()

    async with AsyncParsingSession(translator) as session:
        # Parse multiple characteristics with shared context
        battery = await session.parse(
            BatteryLevelCharacteristic, SIMULATED_BATTERY_DATA
        )
        hr_data = await session.parse(
            HeartRateMeasurementCharacteristic, SIMULATED_HR_DATA
        )

        print(f"Battery: {battery}%")
        print(f"Heart Rate: {hr_data.heart_rate} bpm")


asyncio.run(parsing_session_example())
```

The session maintains context between parses, which is useful for characteristics that depend on each other.

## Migration from Sync API

Migrating is straightforward—add `async`/`await`:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

translator = BluetoothSIGTranslator()
data = bytearray([85])

# Sync (before)
level = translator.parse_characteristic(BatteryLevelCharacteristic, data)

# Async (after) - same API, just awaited
level = await translator.parse_characteristic_async(
    BatteryLevelCharacteristic, data
)
```

Both sync and async methods are available on `BluetoothSIGTranslator`, so you can mix them:

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

SIMULATED_BATTERY_DATA = bytearray([85])


async def mixed_usage():
    translator = BluetoothSIGTranslator()

    # Sync method still works (for quick lookups)
    info = translator.get_characteristic_info_by_uuid("2A19")
    print(f"Characteristic: {info.name}")

    # Async method for parsing
    level = await translator.parse_characteristic_async(
        BatteryLevelCharacteristic, SIMULATED_BATTERY_DATA
    )
    print(f"Battery: {level}%")


asyncio.run(mixed_usage())
```

## See Also

- {py:class}`~bluetooth_sig.core.translator.BluetoothSIGTranslator` - Full API reference
- [Usage Guide](usage.md) - Comprehensive API patterns
- [BLE Integration](ble-integration.md) - Full BLE library integration
- [async BLE example](https://github.com/RonanB96/bluetooth-sig-python/blob/main/examples/async_ble_integration.py)
