# Performance Benchmarking Suite

This repository includes a comprehensive performance benchmarking suite to track and optimize parsing performance.

## Quick Start

Run benchmarks locally:

```bash
# Run all benchmarks
python -m pytest tests/benchmarks/ --benchmark-only

# Generate JSON report
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-json=benchmark.json

# Compare with baseline
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-autosave
# Make changes...
python -m pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001
```

## Benchmark Results

Current performance baseline (Python 3.11, Linux x86_64):

| Operation | Time | Description |
|-----------|------|-------------|
| UUID Resolution | ~190 μs | Lookup characteristic by UUID |
| Simple Parse (uint8) | ~200 μs | Battery Level characteristic |
| Complex Parse (flags) | ~710 μs | Heart Rate with flags |
| Batch (3 chars) | ~4.5 ms | Three characteristics |

See [docs/performance.md](docs/performance.md) for full details.

## CI Integration

Benchmarks run automatically on every PR:
- Regression detection (fails if >2x slower)
- Historical tracking on [GitHub Pages](https://RonanB96.github.io/bluetooth-sig-python/dev/bench/)
- PR comments on performance changes

## What's Benchmarked

- **UUID resolution** - Registry lookup performance
- **Characteristic parsing** - Simple and complex characteristics
- **Batch operations** - Multiple characteristics at once
- **Memory efficiency** - No leaks validation
- **Throughput** - Operations per second

## Interpreting Results

The library overhead (~200 μs per parse) is acceptable for typical BLE use cases:
- Environmental sensors (1 Hz): 0.06% CPU
- Fitness trackers (10 Hz): 1.4% CPU
- Multi-device dashboards (100 devices × 5 chars @ 1 Hz): 10% CPU

BLE I/O typically dominates (10-100ms), making parsing overhead negligible.

## Phase 0: Lazy Loading

All registries now use lazy loading:
- YAML files loaded only on first access
- Reduced import time
- Thread-safe implementation
- Better memory efficiency

## Contributing

When adding new characteristics or features:
1. Run benchmarks before and after changes
2. Document any significant performance impact
3. Consider adding characteristic-specific benchmarks
4. Update docs/performance.md if needed
