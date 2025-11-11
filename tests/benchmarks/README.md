# Benchmarking Guide

This directory contains comprehensive performance benchmarks for the bluetooth-sig library.

## Running Benchmarks

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

## Benchmark Suite

- **UUID resolution** - Registry lookup performance
- **Characteristic parsing** - Simple and complex characteristics
- **Batch operations** - Multiple characteristics at once
- **Memory efficiency** - No leaks validation
- **Library vs manual** - Performance comparison

## Results

See [docs/performance.md](../../docs/performance.md) for detailed performance analysis and baseline metrics.

## CI Integration

Benchmarks run automatically on every PR with regression detection and historical tracking on [GitHub Pages](https://ronanb96.github.io/bluetooth-sig-python/benchmarks/).
