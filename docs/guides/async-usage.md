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
from bluetooth_sig import AsyncBluetoothSIGTranslator

async def main():
    translator = AsyncBluetoothSIGTranslator()
    
    # Single characteristic parsing
    result = await translator.parse_characteristic_async("2A19", data)
    print(f"Battery: {result.value}%")

asyncio.run(main())
```

## Integration with Bleak

[Bleak](https://github.com/hbldh/bleak) is the most popular Python BLE library. Here's how to integrate it with the async translator:

```python
import asyncio
from bleak import BleakClient
from bluetooth_sig import AsyncBluetoothSIGTranslator

async def read_sensor_data(address: str):
    translator = AsyncBluetoothSIGTranslator()
    
    async with BleakClient(address) as client:
        # Read multiple characteristics
        battery_data = await client.read_gatt_char("2A19")
        temp_data = await client.read_gatt_char("2A6E")
        humidity_data = await client.read_gatt_char("2A6F")
        
        # Parse all together
        char_data = {
            "2A19": battery_data,
            "2A6E": temp_data,
            "2A6F": humidity_data,
        }
        
        results = await translator.parse_characteristics_async(char_data)
        
        for uuid, result in results.items():
            print(f"{result.name}: {result.value}")

asyncio.run(read_sensor_data("AA:BB:CC:DD:EE:FF"))
```

## Batch Parsing

The async API automatically optimizes batch parsing:

```python
async def parse_many_characteristics():
    translator = AsyncBluetoothSIGTranslator()
    
    # Small batch (≤5 items) - parsed directly
    small_batch = {
        "2A19": battery_data,
        "2A6E": temp_data,
    }
    results = await translator.parse_characteristics_async(small_batch)
    
    # Large batch (>5 items) - automatically chunked
    # Yields to event loop every 10 characteristics
    large_batch = {f"uuid_{i}": data_i for i in range(50)}
    results = await translator.parse_characteristics_async(large_batch)
```

## Concurrent Parsing

Parse multiple characteristics concurrently using `asyncio.gather`:

```python
async def parse_multiple_devices(devices: list[str]):
    translator = AsyncBluetoothSIGTranslator()
    
    async def read_device(address: str):
        async with BleakClient(address) as client:
            data = await client.read_gatt_char("2A19")
            return await translator.parse_characteristic_async("2A19", data)
    
    # Parse all devices concurrently
    tasks = [read_device(addr) for addr in devices]
    results = await asyncio.gather(*tasks)
    
    return results
```

## Async Context Manager

Maintain parsing context across multiple async operations:

```python
from bluetooth_sig import AsyncBluetoothSIGTranslator, AsyncParsingSession

async def health_monitoring_session(client):
    translator = AsyncBluetoothSIGTranslator()
    async with AsyncParsingSession(translator) as session:
        # Context automatically shared between parses
        hr_data = await client.read_gatt_char("2A37")
        hr_result = await session.parse("2A37", hr_data)
        
        location_data = await client.read_gatt_char("2A38")
        location_result = await session.parse("2A38", location_data)
        
        # location_result has context from hr_result
        print(f"HR: {hr_result.value} at {location_result.value}")
```

## Async Generators

Process streaming characteristic data:

```python
async def monitor_sensor(client):
    translator = AsyncBluetoothSIGTranslator()
    
    async def characteristic_stream():
        """Stream characteristic notifications."""
        while True:
            data = await client.read_gatt_char("2A19")
            yield ("2A19", data)
            await asyncio.sleep(1.0)
    
    async for uuid, data in characteristic_stream():
        result = await translator.parse_characteristic_async(uuid, data)
        print(f"Battery: {result.value}%")
```

## Performance Considerations

The async API:

- **Yields to event loop** - Uses `asyncio.sleep(0)` to allow other tasks to run
- **Enables concurrent operations** - Multiple parse operations can run together
- **No performance penalty** - Small operations have minimal overhead
- **Chunks large batches** - Automatically splits >5 items into chunks of 10

For optimal performance:

- Use batch parsing for multiple characteristics
- Let the library handle concurrency
- Don't create too many concurrent tasks (use `asyncio.Semaphore` if needed)

## API Reference

### AsyncBluetoothSIGTranslator

All methods from [`BluetoothSIGTranslator`][bluetooth_sig.BluetoothSIGTranslator] are available, plus:

- `parse_characteristic_async()` - Async version of [`parse_characteristic`][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic]
- `parse_characteristics_async()` - Async version of [`parse_characteristics`][bluetooth_sig.BluetoothSIGTranslator.parse_characteristics]
- `get_sig_info_by_uuid_async()` - Async version of [`get_sig_info_by_uuid`][bluetooth_sig.BluetoothSIGTranslator.get_sig_info_by_uuid]
- `get_sig_info_by_name_async()` - Async version of [`get_sig_info_by_name`][bluetooth_sig.BluetoothSIGTranslator.get_sig_info_by_name]

### AsyncParsingSession

Context manager for maintaining parsing state:

- `async with AsyncParsingSession(translator) as session:` - Enter async context with a translator
- `await session.parse(uuid, data)` - Parse with accumulated context

## Examples

See the [async BLE integration example](../../examples/async_ble_integration.py) for a complete working example.

## Migration from Sync API

Migrating is straightforward - just add `async`/`await`:

```python
# Before (sync)
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", data)

# After (async)
from bluetooth_sig import AsyncBluetoothSIGTranslator

translator = AsyncBluetoothSIGTranslator()
result = await translator.parse_characteristic_async("2A19", data)
```

Both sync and async methods are available on `AsyncBluetoothSIGTranslator`, so you can mix them:

```python
translator = AsyncBluetoothSIGTranslator()

# Sync method still works
info = translator.get_characteristic_info_by_uuid("2A19")

# Async method
result = await translator.parse_characteristic_async("2A19", data)
```
