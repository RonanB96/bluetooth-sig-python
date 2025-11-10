# Performance Characteristics

Performance benchmarks for the Bluetooth SIG Standards Library.

## Overview

The library is optimized for typical BLE use cases: periodic sensor reads, on-demand queries, and notification parsing. Not optimized for high-frequency streaming (>100 Hz).

## Benchmark Environment

- **Python Version**: 3.11
- **Platform**: Linux x86_64 (GitHub Actions)
- **Timestamp**: Auto-generated with each CI run
- **Consistency**: `PYTHONHASHSEED=0` for reproducible results

## Core Operations

### UUID Resolution

| Operation | Mean | StdDev | Description |
|-----------|------|--------|-------------|
| UUID→Info (short) | ~190 μs | ±10 μs | Lookup by 16-bit UUID (e.g., "2A19") |
| UUID→Info (long) | ~190 μs | ±10 μs | Lookup by 128-bit UUID |
| Name→UUID | ~3.5 μs | ±0.6 μs | Lookup by characteristic name |
| Cached lookup | ~190 μs | ±10 μs | Same as non-cached (registry uses lazy loading) |

**Note**: UUID resolution dominates parsing overhead. Once registries are loaded, lookups are consistently fast (~190 μs).

### Characteristic Parsing

| Characteristic Type | Mean | StdDev | Description |
|---------------------|------|--------|-------------|
| Simple (uint8) | ~200 μs | ±12 μs | Battery Level characteristic |
| Simple (sint16) | ~1.3 ms | ±25 μs | Temperature characteristic |
| Complex (flags) | ~710 μs | ±15 μs | Heart Rate with flags parsing |

**Components of parsing time:**
- UUID resolution: ~190 μs
- Data validation: ~220 ns
- Value decoding: varies by complexity
- Result struct creation: ~6 μs

### Batch Parsing

| Batch Size | Mean (total) | Per-Char | Overhead vs Individual |
|------------|--------------|----------|------------------------|
| 3 chars | ~4.5 ms | ~1.5 ms | Minimal (UUID resolution dominates) |
| 10 chars | ~19 ms | ~1.9 ms | Same as individual |

**Analysis**: Batch parsing doesn't provide significant speedup because:
- Each characteristic requires UUID resolution (~190 μs each)
- No significant fixed overhead to amortize
- Best use case: organizational/API convenience, not performance

## Library vs Manual Parsing

| Operation | Manual | Library | Overhead Factor |
|-----------|--------|---------|-----------------|
| Battery Level | ~288 ns | ~214 μs | 744x |
| Temperature | ~455 ns | ~1.3 ms | 2858x |
| Humidity | ~339 ns | ~751 μs | 2215x |

**Analysis**: The library overhead includes:
- UUID resolution (~190 μs)
- Characteristic lookup and validation
- Type conversion and structured data creation
- Error checking and logging

For most applications, this overhead is negligible compared to BLE I/O latency (typically 10-100ms).

## Overhead Breakdown

| Component | Time |
|-----------|------|
| UUID Resolution | ~189 μs |
| Data Validation | ~220 ns |
| Struct Creation | ~6 μs |

**Total Fixed Overhead**: ~195 μs per characteristic parse
**Variable Cost**: Depends on characteristic complexity

## Throughput

- **Single characteristic**: ~5,000 parses/second (200 μs each)
- **Batch (3 chars)**: ~220 batches/second (~4.5 ms each)
- **Batch (10 chars)**: ~52 batches/second (~19 ms each)
- **UUID resolution**: ~5,300 lookups/second (189 μs each)

## Memory Usage

Based on benchmark observations:
- **Translator instance**: Lightweight (registries use lazy loading)
- **Per-parse overhead**: Minimal (msgspec structs are efficient)
- **No memory leaks**: Validated with 1M parses (200 seconds for 1M parses)

## Real-World Scenarios

These scenarios assume a modern multi-core CPU (e.g., Intel Core i5/i7 or equivalent) where 1 core = 100% CPU.

### Scenario 1: Environmental Sensor (1 Hz)
```
Temperature (1 Hz) + Humidity (1 Hz) + Pressure (1 Hz)
= 3 parses/second × 200 μs/parse = 600 μs/second CPU time
= 0.06% of one CPU core
```

### Scenario 2: Fitness Tracker (10 Hz notifications)
```
Heart Rate (10 Hz) + Running Speed (10 Hz)
= 20 parses/second × 700 μs/parse = 14 ms/second CPU time
= 1.4% of one CPU core
```

### Scenario 3: Multi-Device Dashboard (100 devices)
```
100 devices × 5 characteristics × 1 Hz = 500 parses/second
= 500 × 200 μs = 100 ms/second CPU time
= 10% of one CPU core
```

**Note**: CPU utilization percentages are theoretical estimates based on parsing time alone. Actual utilization will include BLE I/O overhead, framework overhead, and other application logic. BLE I/O typically dominates at 10-100ms per operation.

## Optimization Guidelines

### When Performance Matters
- Profile first - identify actual bottlenecks
- Consider caching characteristic instances
- Parse only needed characteristics
- Use async variants for I/O-bound operations
- For high-frequency applications (>100 Hz), consider manual parsing

### When Performance Doesn't Matter
- Single device, low frequency (<10 Hz)
- Small number of characteristics (<10)
- BLE I/O dominates (typically 10-100ms per operation)
- Focus on correctness and maintainability over micro-optimizations

## Regression Detection

CI runs benchmarks on every commit and fails if:
- Any operation >2x slower than baseline (200% threshold)
- Consistent degradation across multiple operations
- Memory usage increases significantly

## Running Benchmarks Locally

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

## Historical Performance Tracking

View historical benchmark data: [GitHub Pages Dashboard](https://RonanB96.github.io/bluetooth-sig-python/dev/bench/)

The dashboard provides:
- Interactive charts showing performance trends
- Commit-level drill-down for regression analysis
- Comparison across different test runs
- Download capability for historical data

## Benchmark Maintenance

To ensure benchmark reliability:
- Run on consistent hardware (GitHub Actions standard runners)
- Use fixed Python hash seed (`PYTHONHASHSEED=0`)
- Avoid external I/O during benchmarks
- Use multiple iterations for statistical significance
- Document any environmental changes in git history
