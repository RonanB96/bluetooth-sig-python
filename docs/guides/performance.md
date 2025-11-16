# Performance Guide

Tips for optimizing performance when using the Bluetooth SIG Standards
Library.

## Performance Characteristics

### Typical Performance

- **UUID resolution**: ~10 μs
- **Simple characteristic parse**: ~50 μs
- **Complex characteristic parse**: ~200 μs
- **Memory footprint**: Minimal (< 10 MB)

### Bottlenecks

The library is optimized for parsing speed. Typical bottlenecks are:

1. **BLE I/O operations** - Reading from device (milliseconds)
1. **Network latency** - For remote devices
1. **Connection management** - Device discovery and pairing

The parsing itself is rarely the bottleneck.

## Optimization Tips

### 1. Reuse Translator Instance

```python
# SKIP: Example requires external sensor_readings and uuid variables
from bluetooth_sig import BluetoothSIGTranslator

# ✅ Good - create once, reuse
translator = BluetoothSIGTranslator()
for data in sensor_readings:
    result = translator.parse_characteristic(uuid, data)

# ❌ Bad - creating new instances
for data in sensor_readings:
    translator = BluetoothSIGTranslator()  # Wasteful
    result = translator.parse_characteristic(uuid, data)
```

### 2. Batch Operations

When reading multiple characteristics, batch the BLE operations:

```python
# SKIP: Example requires BLE hardware access and external uuids variable
from bluetooth_sig import BluetoothSIGTranslator

# ✅ Good - batch read, then parse
async with BleakClient(address) as client:
    # Read all characteristics at once
    battery_data = await client.read_gatt_char("2A19")
    temp_data = await client.read_gatt_char("2A6E")
    humidity_data = await client.read_gatt_char("2A6F")

    # Parse offline
    battery = translator.parse_characteristic("2A19", battery_data)
    temp = translator.parse_characteristic("2A6E", temp_data)
    humidity = translator.parse_characteristic("2A6F", humidity_data)

# ❌ Bad - connect/disconnect for each
for uuid in uuids:
    async with BleakClient(address) as client:
        data = await client.read_gatt_char(uuid)
        result = translator.parse_characteristic(uuid, data)
```

### 3. Use Direct Characteristic Classes

For repeated parsing of the same characteristic type:

```python
# SKIP: Example requires external battery_readings variable
# ✅ Good - direct characteristic access
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery_char = BatteryLevelCharacteristic()
for data in battery_readings:
    value = battery_char.decode_value(data)

# ⚠️ Slower - goes through translator
translator = BluetoothSIGTranslator()
for data in battery_readings:
    result = translator.parse_characteristic("2A19", data)
```

### 4. Avoid Unnecessary Conversions

```python
# ✅ Good - use bytearray directly
data = bytearray([85])
result = translator.parse_characteristic("2A19", data)

# ❌ Bad - unnecessary conversion
data = bytes([85])
result = translator.parse_characteristic("2A19", bytearray(data))
```

## Profiling

To identify bottlenecks in your application:

```python
# SKIP: Profiling example that creates files and performs extensive operations
import cProfile
import pstats
from bluetooth_sig import BluetoothSIGTranslator

def profile_parsing():
    translator = BluetoothSIGTranslator()
    data = bytearray([75])

    # Run many iterations
    for _ in range(10000):
        translator.parse_characteristic("2A19", data)

# Profile
cProfile.run('profile_parsing()', 'stats.prof')

# View results
stats = pstats.Stats('stats.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Memory Optimization

### Registry Caching

The registry is loaded once and cached. This is automatic and requires
no configuration.

### Cleanup

For long-running applications, there's minimal memory accumulation. No special
cleanup needed.

## Concurrent Operations

The library is thread-safe for reading operations:

```python
# SKIP: Example requires external sensor_data variable
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

def parse_in_thread(uuid, data):
    return translator.parse_characteristic(uuid, data)

# Parallel parsing (though rarely needed)
with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(parse_in_thread, uuid, data)
            for uuid, data in sensor_data.items()
        ]
        results = [
            f.result() for f in futures
        ]
```

**Note**: Parsing is so fast that parallelization rarely provides benefits.
Focus on parallelizing BLE I/O operations instead.

## Real-World Performance

In typical applications:

```python
import time
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Time 1000 parses
start = time.perf_counter()
for _ in range(1000):
    translator.parse_characteristic("2A19", bytearray([75]))
elapsed = time.perf_counter() - start

print(f"1000 parses in {elapsed:.3f}s")
print(
    f"Average: {elapsed * 1000:.1f}μs per parse"
)
# Typical output: "1000 parses in 0.050s" (50μs avg)
```

The parsing overhead is negligible compared to BLE operations (typically
10-100ms per read).

## Recommendations

1. **Focus on BLE optimization** - Connection management, batching
1. **Reuse translator instances** - Create once, use many times
1. **Profile your application** - Identify real bottlenecks
1. **Don't over-optimize** - Parsing is already fast

## See Also

- [BLE Integration](ble-integration.md) - Optimize BLE operations
- [Architecture](../architecture/index.md) - Understand the design
- [Testing Guide](../testing.md) - Performance testing
