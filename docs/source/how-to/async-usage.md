# Async Usage Guide

Learn how to use the async API variants for non-blocking parsing.

## When to Use Async

Use the async API when:

- Working with async BLE libraries (bleak, etc.)
- Parsing large batches of characteristics
- Building async applications (FastAPI, asyncio-based)
- Need concurrent parsing operations

The async API maintains full backward compatibility - all sync methods remain available.

## Basic Async Usage

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytes([75])  # Simulates 75% battery level


async def main():
    translator = BluetoothSIGTranslator()

    # You get UUIDs from your BLE library - you don't need to know what they mean!
    # The library will auto-identify them
    battery_uuid = "2A19"  # From BLE scan/discovery

    # Parse and auto-identify
    result = await translator.parse_characteristic_async(
        battery_uuid, SIMULATED_BATTERY_DATA
    )
    print(f"Discovered: {result.info.name}")  # "Battery Level"
    print(f"{result.info.name}: {result.value}%")

    # Alternative: If you know the characteristic, convert enum to UUID first
    from bluetooth_sig.types.gatt_enums import CharacteristicName

    battery_uuid = translator.get_characteristic_uuid_by_name(
        CharacteristicName.BATTERY_LEVEL
    )
    if battery_uuid:
        result2 = await translator.parse_characteristic_async(
            str(battery_uuid), SIMULATED_BATTERY_DATA
        )
        print(f"Using enum: {result2.info.name} = {result2.value}%")


asyncio.run(main())
```

## Integration with Bleak

[Bleak](https://github.com/hbldh/bleak) is the most popular Python BLE library. Here's how to integrate it:

```python
import asyncio

from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator


# SKIP: Async function with parameters - callback pattern
async def read_sensor_data(address: str):
    translator = BluetoothSIGTranslator()

    async with BleakClient(address) as client:
        # Bleak gives you UUIDs from device discovery - you don't need to know what they are!
        battery_uuid = "2A19"  # From client.services
        battery_data = await client.read_gatt_char(battery_uuid)

        # bluetooth-sig auto-identifies and parses
        result = await translator.parse_characteristic_async(
            battery_uuid, battery_data
        )
        print(f"Discovered: {result.info.name}")  # "Battery Level"
        print(f"{result.info.name}: {result.value}%")

        # Batch parsing multiple characteristics
        temp_uuid = "2A6E"  # From client.services
        humidity_uuid = "2A6F"  # From client.services

        char_data = {
            battery_uuid: await client.read_gatt_char(battery_uuid),
            temp_uuid: await client.read_gatt_char(temp_uuid),
            humidity_uuid: await client.read_gatt_char(humidity_uuid),
        }

        results = await translator.parse_characteristics_async(char_data)

        for uuid, result in results.items():
            print(f"{result.name}: {result.value} {result.unit or ''}")


# ============================================
# SIMULATED DATA - Replace with actual device
# ============================================
SIMULATED_DEVICE_ADDRESS = (
    "AA:BB:CC:DD:EE:FF"  # Example MAC address - use your actual device
)

asyncio.run(read_sensor_data(SIMULATED_DEVICE_ADDRESS))
```

## Batch Parsing

Batch parse multiple characteristics in a single async call:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName


async def parse_many_characteristics():
    translator = BluetoothSIGTranslator()

    # Get UUIDs from enums
    battery_uuid = "2A19"
    temp_uuid = "2A6E"
    humidity_uuid = "2A6F"

    # Parse multiple characteristics together
    char_data = {
        battery_uuid: battery_data,
        temp_uuid: temp_data,
        humidity_uuid: humidity_data,
    }
    results = await translator.parse_characteristics_async(char_data)

    for uuid, result in results.items():
        print(f"{result.name}: {result.value} {result.unit or ''}")
```

## Concurrent Parsing

Parse multiple devices concurrently using `asyncio.gather`:

```python
from bleak import BleakClient

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName


async def parse_multiple_devices(devices: list[str]):
    translator = BluetoothSIGTranslator()
    battery_uuid = "2A19"

    async def read_device(address: str):
        async with BleakClient(address) as client:
            data = await client.read_gatt_char(battery_uuid)
            return await translator.parse_characteristic_async(
                battery_uuid, data
            )

    # Parse all devices concurrently
    tasks = [read_device(addr) for addr in devices]
    results = await asyncio.gather(*tasks)

    return results
```

## Async Context Manager

Maintain parsing context across multiple async operations:

```python
from bluetooth_sig import AsyncParsingSession, BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName


async def health_monitoring_session(client):
    translator = BluetoothSIGTranslator()

    async with AsyncParsingSession(translator) as session:
        # Get UUIDs from enums
        hr_uuid = "2A37"
        location_uuid = CharacteristicName.BODY_SENSOR_LOCATION.get_uuid()

        hr_data = await client.read_gatt_char(hr_uuid)
        hr_result = await session.parse(hr_uuid, hr_data)

        location_data = await client.read_gatt_char(location_uuid)
        location_result = await session.parse(location_uuid, location_data)

        # Context automatically shared between parses
        print(f"HR: {hr_result.value} at {location_result.value}")
```

## Async Generators

Process streaming characteristic data:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName


async def monitor_sensor(client):
    translator = BluetoothSIGTranslator()
    battery_uuid = "2A19"

    async def characteristic_stream():
        """Stream characteristic notifications."""
        while True:
            data = await client.read_gatt_char(battery_uuid)
            yield (battery_uuid, data)
            await asyncio.sleep(1.0)

    async for uuid, data in characteristic_stream():
        result = await translator.parse_characteristic_async(uuid, data)
        print(f"{result.name}: {result.value}%")
```

## Performance Considerations

The async API:

- **Async-compatible wrappers** - Methods can be awaited in async contexts
- **Synchronous parsing** - Actual parsing is CPU-bound and runs synchronously
- **No performance penalty** - Fast parsing operations with no overhead
- **Enables async workflows** - Integrates seamlessly with async BLE libraries

For optimal performance:

- Use batch parsing for multiple characteristics
- Combine with async I/O operations (BLE reads/writes)
- Don't create too many concurrent tasks (use `asyncio.Semaphore` if needed)

## API Reference

### BluetoothSIGTranslator

All methods from {py:class}`~bluetooth_sig.core.translator.BluetoothSIGTranslator` are available, plus:

- `parse_characteristic_async()` - Async-compatible wrapper for `parse_characteristic`
- `parse_characteristics_async()` - Async-compatible wrapper for `parse_characteristics`

Note: Use the inherited sync methods directly for simple lookups like `get_sig_info_by_uuid()` and `get_sig_info_by_name()` as they don't perform I/O.

### AsyncParsingSession

Context manager for maintaining parsing state:

- `async with AsyncParsingSession(translator) as session:` - Enter async context with a translator
- `await session.parse(uuid, data)` - Parse with accumulated context

## Examples

See the [async BLE integration example](https://github.com/RonanB96/bluetooth-sig-python/blob/main/examples/async_ble_integration.py) for a complete working example.

## Migration from Sync API

Migrating is straightforward - just add `async`/`await`:

```python
# Before (sync)
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()
battery_uuid = "2A19"
result = translator.parse_characteristic(battery_uuid, data)

# After (async)
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()
battery_uuid = "2A19"
result = await translator.parse_characteristic_async(battery_uuid, data)
```

Both sync and async methods are available on `BluetoothSIGTranslator`, so you can mix them:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()
battery_uuid = "2A19"

# Sync method still works
info = translator.get_characteristic_info_by_uuid(battery_uuid)

# Async method
result = await translator.parse_characteristic_async(battery_uuid, data)
```
