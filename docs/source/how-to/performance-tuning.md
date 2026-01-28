# Performance Tuning

Learn how to optimize the Bluetooth SIG Standards Library for your use case.

## When Performance Matters

Consider optimization when:

- High-frequency parsing (>100 Hz notifications)
- Processing many devices simultaneously (>50 devices)
- CPU-constrained environments (embedded systems, edge devices)
- Real-time requirements with tight latency constraints

## When Performance Doesn't Matter

Skip optimization for:

- Single device, low frequency (<10 Hz)
- Small number of characteristics (<10)
- BLE I/O dominates (typically 10-100ms per operation)
- Focus on correctness and maintainability over micro-optimizations

The library overhead (~200 μs per parse) is negligible compared to typical BLE I/O latency (10-100ms).

## Optimization Strategies

### 1. Profile First

Always identify actual bottlenecks before optimizing:

```python
import cProfile
import pstats

from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Profile your code
profiler = cProfile.Profile()
profiler.enable()

# Your BLE parsing code here
for _ in range(1000):
    result = translator.parse_characteristic("2A19", bytearray([75]))

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)
```

### 2. Cache Characteristic Instances

For frequently-used characteristics, consider caching:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Cache characteristic info to avoid repeated UUID lookups
battery_info = translator.get_sig_info_by_uuid("2A19")
temp_info = translator.get_sig_info_by_uuid("2A6E")

# Later, use cached info
# (Note: Current API doesn't expose direct parsing with cached info,
# but you can reuse UUID strings)
battery_uuid = "2A19"
result = translator.parse_characteristic(battery_uuid, data)
```

### 3. Parse Only Needed Characteristics

Don't parse characteristics you won't use:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

translator = BluetoothSIGTranslator()

# Example: Device sends many characteristics, but we only need a few
all_notifications = [
    ("2A19", bytearray([75])),  # Battery Level - NEEDED
    ("2A6E", bytearray([0x54, 0x09])),  # Temperature - NEEDED
    ("2A6F", bytearray([0x54, 0x09])),  # Humidity - NEEDED
    # System ID requires 8 bytes
    ("2A23", bytearray([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0])),
    ("2A29", bytearray([0x41, 0x63, 0x6D, 0x65])),  # Manufacturer Name
    ("2A50", bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])),  # PnP ID
]

# ❌ Bad: Parse everything (wastes CPU on unused characteristics)
for char_uuid, data in all_notifications:
    try:
        result = translator.parse_characteristic(char_uuid, data)
    except CharacteristicParseError:
        pass  # Handle parse failures
    # Parsed 6 characteristics but only use 3

# ✅ Good: Parse selectively (only what you need)
MONITORED_CHARS = {"2A19", "2A6E", "2A6F"}  # Battery, Temp, Humidity
for char_uuid, data in all_notifications:
    if char_uuid in MONITORED_CHARS:
        result = translator.parse_characteristic(char_uuid, data)
```

### 4. Use Async for I/O-Bound Operations

When BLE I/O dominates, use async variants:

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def process_device(device_address: str):
    translator = BluetoothSIGTranslator()

    async with BleakClient(device_address) as client:
        # Read multiple characteristics concurrently
        battery_data = await client.read_gatt_char("2A19")
        temp_data = await client.read_gatt_char("2A6E")

        # Parse (these are fast, no await needed)
        battery = translator.parse_characteristic("2A19", battery_data)
        temp = translator.parse_characteristic("2A6E", temp_data)
```

### 5. Consider Manual Parsing for Hot Paths

For ultra-high-frequency parsing (>1000 Hz), manual parsing may be faster:

```python
# Library overhead: ~200 μs per parse
result = translator.parse_characteristic("2A19", data)

# Manual parsing: ~300 ns (no UUID resolution, no validation)
battery_level = data[0]  # uint8, range 0-100
```

**Trade-off**: Lose automatic validation, UUID resolution, and structured data.

<a id="running-benchmarks-locally"></a>

## Running Benchmarks Locally

Profile your changes against the baseline:

```bash
# Run all benchmarks
python -m pytest tests/benchmarks/ --benchmark-only

# Run with detailed output
python -m pytest tests/benchmarks/ --benchmark-only -v

# Generate JSON report
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-json=benchmark.json

# Save baseline
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-autosave

# Compare with baseline
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001

# Fail if performance degrades >200%
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001 --benchmark-compare-fail=mean:200%
```

## Future Optimizations

Potential improvements (if needed):

1. **Cython compilation** for critical parsing paths
2. **Registry caching** for frequently-used characteristics
3. **Pre-compiled struct parsing** for fixed-format characteristics
4. **Parallel batch parsing** for large batches
5. **numpy integration** for bulk data processing

**Note**: Current performance is adequate for typical use cases. Optimizations should be driven by real-world performance requirements.

## Performance Targets

Based on common BLE use cases:

| Use Case | Parsing Frequency | Target Overhead | Status |
|----------|-------------------|-----------------|--------|
| Environmental sensor | 1 Hz | <1 ms | ✅ ~200 μs |
| Fitness tracker | 10 Hz | <10 ms | ✅ ~700 μs |
| Multi-device (10) | 10 Hz each | <100 ms | ✅ ~7 ms |
| High-frequency (100 Hz) | 100 Hz | <1 ms | ⚠️ Consider manual |

## Performance Metrics

For detailed performance data and benchmarks:

- [Performance Benchmark Data](../performance/performance-data.md)
- [Live Benchmarks](../performance/benchmarks.md)

## See Also

- [API Reference](../api/index.md) - Complete API documentation
- [Testing Guide](testing.md) - How to test performance in your application
