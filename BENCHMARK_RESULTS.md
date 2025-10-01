# Benchmark Results Summary

This document contains benchmark results for the Bluetooth SIG library parsing performance.

## Test Environment

- Python: 3.11.13
- Platform: Linux
- Test Date: October 2025
- Iterations: 10,000 for single operations, 1,000 for batch operations

## Performance Overview

| Metric | Value |
|--------|-------|
| Average Latency | 0.0425ms per operation |
| Average Throughput | 47,641 operations/sec |
| Logging Overhead (DEBUG) | ~10-20% |
| Logging Overhead (INFO) | ~5-10% |

## Single Characteristic Parsing

### Battery Level (1 byte, simple)

```
Implementation                 Avg Time        Throughput           vs Baseline
--------------------------------------------------------------------------------
manual                         0.0002ms        4,240,880 ops/sec    (baseline)
sig_library                    0.0099ms        100,966 ops/sec      42.00x slower
```

**Analysis**: Manual parsing is faster but provides only raw value. SIG library adds:
- Unit conversion (%)
- Validation
- Type safety
- Error handling

### Temperature (2 bytes, moderate)

```
Implementation                 Avg Time        Throughput           vs Baseline
--------------------------------------------------------------------------------
manual                         0.0004ms        2,731,305 ops/sec    (baseline)
sig_library                    0.0206ms        48,601 ops/sec       56.20x slower
```

**Analysis**: Manual parsing extracts value only. SIG library provides:
- Temperature conversion
- Unit handling (°C)
- Validation
- Type information

### Heart Rate (complex with flags)

```
Implementation                 Avg Time        Throughput           vs Baseline
--------------------------------------------------------------------------------
manual                         0.0003ms        3,894,072 ops/sec    (baseline)
sig_library                    0.0691ms        14,481 ops/sec       268.92x slower
```

**Analysis**: Heart rate requires flag parsing. Manual implementation is minimal.
SIG library provides:
- Flag interpretation
- Contact detection
- Energy expenditure
- RR intervals
- All validation

## Batch Parsing

```
Implementation                 Avg Time        Throughput           vs Baseline
--------------------------------------------------------------------------------
batch                          0.1131ms        8,840 ops/sec        1.11x slower
individual                     0.1017ms        9,835 ops/sec        (baseline)
```

**Analysis**: Batch parsing has minimal overhead (11%). Benefits:
- Cleaner code
- Better for 4+ characteristics
- Shared context handling
- Single API call

## UUID Resolution

```
Implementation                 Avg Time        Throughput
--------------------------------------------------------------------------------
uuid_lookup                    0.0126ms        79,340 ops/sec
name_resolution                0.0010ms        971,231 ops/sec
```

**Analysis**: Name resolution is 12x faster than UUID lookup.

## Real-World Scenario

**Scenario**: Health thermometer sending temperature notifications every 1 second

```
Iterations: 5,000
Total time: 0.1487s
Average:    0.0297ms per operation
Min:        0.0276ms
Max:        0.1079ms
Throughput: 33,616 ops/sec
```

**Analysis**:
- CPU time per notification: 0.0297ms (0.003% of 1-second interval)
- Could handle 33,616 concurrent devices on single thread
- Minimal overhead for typical BLE applications

## Performance vs Features Trade-off

### Manual Parsing

**Pros:**
- Fastest (0.0002-0.0004ms)
- Minimal overhead
- Direct value extraction

**Cons:**
- No validation
- No unit conversion
- No error handling
- Maintenance burden
- No standards compliance

### SIG Library

**Pros:**
- Standards compliant
- Full validation
- Unit conversion
- Type safety
- Error handling
- Maintainable

**Cons:**
- Slower (0.01-0.07ms)
- More overhead

**Trade-off Analysis**: For 99% of BLE applications, the 0.01-0.07ms overhead is negligible compared to:
- BLE connection latency: 10-100ms
- Notification interval: 100-1000ms
- Network operations: 100-1000ms

## Optimization Recommendations

### 1. High-Throughput (>1000 ops/sec)

```python
# Use batch parsing
sensor_data = {
    "2A19": battery_data,
    "2A6E": temp_data,
    "2A6F": humidity_data,
}
results = translator.parse_characteristics(sensor_data)
```

### 2. Low-Latency (<1ms requirement)

```python
# Reuse translator instance
translator = BluetoothSIGTranslator()
# Disable logging in production
logging.getLogger("bluetooth_sig").setLevel(logging.WARNING)
```

### 3. Memory-Constrained

```python
# Clear caches periodically
translator.clear_services()
```

### 4. Many Devices

```python
# Cache characteristic info
char_info = translator.get_characteristic_info("2A19")
# Reuse for all devices
```

## Conclusion

The Bluetooth SIG library provides comprehensive standards-compliant parsing with minimal performance overhead. For typical BLE applications:

- **Latency impact**: <0.1ms per operation (negligible vs BLE latency)
- **CPU usage**: <0.01% per notification
- **Scalability**: Can handle 30,000+ concurrent devices

The trade-off between manual parsing speed and library features heavily favors using the library for:
- Standards compliance
- Maintainability
- Robustness
- Development speed

Manual parsing should only be considered for:
- Ultra-low-latency requirements (<0.1ms)
- Extremely high throughput (>100k ops/sec)
- Resource-constrained embedded systems

## Running Benchmarks

To reproduce these results:

```bash
# Full benchmark
python examples/benchmarks/parsing_performance.py

# With logging overhead measurement
python examples/benchmarks/parsing_performance.py --log-level=debug

# Quick benchmark
python examples/benchmarks/parsing_performance.py --quick
```

See [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md) for detailed performance guide and optimization strategies.
