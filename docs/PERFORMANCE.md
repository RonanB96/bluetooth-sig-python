# Performance Profiling and Optimization Guide

This guide covers performance characteristics, profiling tools, and optimization strategies for the Bluetooth SIG library.

## Quick Start

### Running Benchmarks

Run the comprehensive benchmark suite:

```bash
python examples/benchmarks/parsing_performance.py
```

Run with logging enabled to see detailed parsing information:

```bash
python examples/benchmarks/parsing_performance.py --log-level=debug
```

### Enabling Logging in Your Application

```python
import logging
from bluetooth_sig import BluetoothSIGTranslator

# Configure logging - can be set to DEBUG, INFO, WARNING, ERROR
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Or configure just the bluetooth_sig logger
logging.getLogger("bluetooth_sig.core.translator").setLevel(logging.DEBUG)

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", bytes([100]))
# Logs: "Parsing characteristic UUID=2A19, data_len=1"
# Logs: "Found parser for UUID=2A19: BatteryLevelCharacteristic"
# Logs: "Successfully parsed Battery Level: 100"
```

## Profiling Utilities

The library includes profiling utilities in `bluetooth_sig.utils.profiling`:

### Timer Context Manager

```python
from bluetooth_sig.utils.profiling import timer

with timer("parse operation") as t:
    result = translator.parse_characteristic("2A19", data)

print(f"Parse took {t['elapsed']:.4f} seconds")
```

### Benchmark Function

```python
from bluetooth_sig.utils.profiling import benchmark_function

result = benchmark_function(
    lambda: translator.parse_characteristic("2A19", data),
    iterations=10000,
    operation="Battery Level parsing"
)

print(result)  # Shows avg, min, max times and throughput
```

### Compare Implementations

```python
from bluetooth_sig.utils.profiling import compare_implementations, format_comparison

results = compare_implementations(
    {
        "manual": lambda: manual_parse(data),
        "sig_lib": lambda: translator.parse_characteristic("2A19", data)
    },
    iterations=10000
)

print(format_comparison(results, baseline="manual"))
```

### Profiling Session

Track multiple benchmarks in a session:

```python
from bluetooth_sig.utils.profiling import ProfilingSession

session = ProfilingSession(name="My Application Benchmarks")

# Add results from various benchmarks
session.add_result(result1)
session.add_result(result2)

print(session)  # Pretty-printed summary of all results
```

## Performance Characteristics

### Parsing Latency

Based on benchmark results with 10,000 iterations:

| Characteristic Type | Complexity | Avg Latency | Throughput |
|-------------------|------------|-------------|------------|
| Battery Level | Simple (1 byte) | 0.01ms | ~100k ops/sec |
| Temperature | Moderate (2 bytes) | 0.02ms | ~48k ops/sec |
| Heart Rate | Complex (flags) | 0.07ms | ~14k ops/sec |

### Batch Processing

Batch parsing (`parse_characteristics`) has minimal overhead:
- Individual parsing: 0.10ms per characteristic
- Batch parsing: 0.11ms per characteristic (11% overhead)
- Batch overhead is amortized - better for 10+ characteristics

### Real-World Performance

For a health thermometer device sending notifications every 1 second:
- Parse latency: ~0.03ms
- CPU usage: 0.003% per notification
- Could handle 30,000+ concurrent devices on a single thread

### Logging Overhead

Logging impact on performance:
- **Disabled** (WARNING level): baseline performance
- **INFO level**: ~5-10% overhead
- **DEBUG level**: ~10-20% overhead

**Recommendation**: Use WARNING level in production, DEBUG only for troubleshooting.

## Optimization Strategies

### 1. High-Throughput Applications

For applications processing many notifications per second:

```python
# ✅ Good: Batch processing
sensor_data = {
    "2A19": battery_data,
    "2A6E": temp_data,
    "2A6F": humidity_data,
}
results = translator.parse_characteristics(sensor_data)

# ❌ Avoid: Processing one at a time in a tight loop
for uuid, data in sensor_data.items():
    result = translator.parse_characteristic(uuid, data)
```

### 2. Low-Latency Applications

For real-time applications requiring minimal latency:

```python
# ✅ Good: Reuse translator instance
translator = BluetoothSIGTranslator()
# Use the same instance for all parses

# ❌ Avoid: Creating new translator for each parse
result = BluetoothSIGTranslator().parse_characteristic(uuid, data)
```

### 3. Memory Optimization

For applications handling many devices:

```python
translator = BluetoothSIGTranslator()

# Process device data...

# Periodically clear cached services if tracking many devices
translator.clear_services()
```

### 4. Caching Characteristic Info

If repeatedly parsing the same characteristic types:

```python
# Cache characteristic info at startup
char_info = translator.get_characteristic_info("2A19")

# Use cached info to validate before parsing
if char_info:
    result = translator.parse_characteristic("2A19", data)
```

## Hot Code Paths

Based on profiling, these are the most frequently executed code paths:

1. **`CharacteristicRegistry.create_characteristic`** - UUID lookup
   - Optimize by minimizing unique UUID types
   - Cache characteristic instances if possible

2. **`Characteristic.parse_value`** - Parsing logic
   - Most time spent here is unavoidable (actual parsing)
   - Consider manual parsing for ultra-low-latency requirements

3. **Context building** - In batch operations
   - Overhead is minimal but scales with batch size
   - Use context only when needed (device info, cross-char references)

## Profiling Your Application

### Example: Profile Device Connection Flow

```python
from bluetooth_sig.utils.profiling import ProfilingSession, benchmark_function

session = ProfilingSession(name="Device Connection Profile")

# Profile discovery
discovery_result = benchmark_function(
    lambda: discover_devices(),
    iterations=10,
    operation="Device discovery"
)
session.add_result(discovery_result)

# Profile connection
connect_result = benchmark_function(
    lambda: connect_to_device(device_id),
    iterations=10,
    operation="Device connection"
)
session.add_result(connect_result)

# Profile parsing
parse_result = benchmark_function(
    lambda: translator.parse_characteristics(char_data),
    iterations=100,
    operation="Parse all characteristics"
)
session.add_result(parse_result)

# Print comprehensive report
print(session)
```

## Logging Levels

### DEBUG

Most verbose - shows every parse operation:

```
2025-10-01 10:00:00,123 - bluetooth_sig.core.translator - DEBUG - Parsing characteristic UUID=2A19, data_len=1
2025-10-01 10:00:00,124 - bluetooth_sig.core.translator - DEBUG - Found parser for UUID=2A19: BatteryLevelCharacteristic
2025-10-01 10:00:00,125 - bluetooth_sig.core.translator - DEBUG - Successfully parsed Battery Level: 100
```

**Use for**: Development, troubleshooting parsing issues

### INFO

High-level information about operations:

```
2025-10-01 10:00:00,123 - bluetooth_sig.core.translator - INFO - No parser available for UUID=unknown-uuid
```

**Use for**: Monitoring, identifying missing parsers

### WARNING

Parse failures and issues:

```
2025-10-01 10:00:00,123 - bluetooth_sig.core.translator - WARNING - Parse failed for Temperature: Data too short
```

**Use for**: Production monitoring, alerting

### ERROR

Critical errors only:

**Use for**: Production (minimal overhead)

## Benchmark Results

The comprehensive benchmark (`examples/benchmarks/parsing_performance.py`) provides:

1. **Single characteristic parsing** - Compare manual vs library parsing
2. **Batch parsing** - Evaluate batch vs individual parsing
3. **UUID resolution** - Measure lookup performance
4. **Real-world scenario** - Simulated device interaction

### Sample Output

```
Profile: Parsing Performance Benchmark
Total operations measured: 6

Average performance across all tests:
  Latency:    0.0425ms per operation
  Throughput: 47,641 operations/sec

OPTIMIZATION RECOMMENDATIONS:
1. Use batch parsing when possible
2. Library adds minimal overhead (<0.1ms for simple characteristics)
3. Reuse translator instances
4. Enable logging only for debugging
```

## When to Use Manual Parsing

Consider manual parsing if:

1. **Ultra-low latency required** - Library adds ~0.01-0.07ms overhead
2. **Simple characteristic** - Battery level (1 byte) is trivial to parse manually
3. **Custom format** - Non-standard or proprietary characteristics

Otherwise, use the library for:
- **Standards compliance** - Handles all SIG specification details
- **Maintainability** - No need to understand binary formats
- **Robustness** - Built-in validation and error handling
- **Features** - Units, types, timestamps, status codes

## Contributing Optimizations

If you identify performance bottlenecks:

1. Run the benchmark: `python examples/benchmarks/parsing_performance.py`
2. Use profiling tools to identify hot spots
3. Propose optimizations with benchmark comparisons
4. Submit PR with before/after performance data

## See Also

- [`examples/benchmarks/parsing_performance.py`](../examples/benchmarks/parsing_performance.py) - Comprehensive benchmark
- [`src/bluetooth_sig/utils/profiling.py`](../src/bluetooth_sig/utils/profiling.py) - Profiling utilities API
- [`tests/test_profiling.py`](../tests/test_profiling.py) - Profiling utility tests
- [`tests/test_logging.py`](../tests/test_logging.py) - Logging functionality tests
