"""Performance tracking tests to monitor parsing speed over time.

CURRENTLY DISABLED: These tests are skipped pending implementation of proper
performance tracking infrastructure.

ISSUES WITH CURRENT APPROACH:
- No historical data storage or comparison against previous runs
- Arbitrary thresholds don't represent actual baseline performance
- CI timing variability causes flaky tests
- Unit tests are wrong tool for performance tracking (need benchmarks)
- Only catches catastrophic (10x+) regressions, misses gradual degradation

TODO: Implement proper performance tracking:
- Use pytest-benchmark with historical storage (.benchmarks/ directory)
- Compare against previous runs with statistical analysis
- Run on dedicated hardware, not in shared CI
- Generate trend reports and visualizations
- Store baseline metrics for regression detection

For now, use profiling tools locally (cProfile, py-spy) for performance analysis.
"""

from __future__ import annotations

import time

import pytest

from bluetooth_sig import BluetoothSIGTranslator

# Skip all tests in this file until proper performance tracking is implemented
pytestmark = pytest.mark.skip(
    reason="Performance tracking disabled - needs proper benchmark infrastructure with historical data storage"
)


class TestPerformanceTracking:
    """Track parsing performance to detect regressions."""

    @pytest.fixture
    def translator(self):
        """Create a translator instance for testing."""
        return BluetoothSIGTranslator()

    def test_battery_level_parse_performance(self, translator):
        """Track battery level parsing performance (baseline: <5ms).

        This test establishes a performance baseline. The threshold is
        intentionally generous to avoid false failures on slower systems
        while still catching major regressions (e.g., 10x+ slowdowns).
        """
        battery_data = bytes([0x64])  # 100%
        iterations = 1000

        # Warmup
        for _ in range(10):
            translator.parse_characteristic("2A19", battery_data)

        # Measure
        start = time.perf_counter()
        for _ in range(iterations):
            result = translator.parse_characteristic("2A19", battery_data)
            assert result.parse_success  # Ensure parsing works
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Generous baseline to accommodate various system speeds
        # Flag only truly pathological performance (>5ms for simple parse)
        assert avg_time_ms < 5.0, (
            f"Battery level parsing excessively slow: {avg_time_ms:.4f}ms avg "
            f"(expected <5.0ms). Total: {elapsed:.4f}s for {iterations} iterations. "
            f"This indicates a major performance regression."
        )

    def test_temperature_parse_performance(self, translator):
        """Track temperature parsing performance (baseline: <10ms).

        This test establishes a performance baseline for moderate complexity
        characteristics. Threshold is generous to avoid system-dependent failures.
        """
        temp_data = bytes([0x64, 0x09])  # 24.20°C
        iterations = 1000

        # Warmup
        for _ in range(10):
            translator.parse_characteristic("2A6E", temp_data)

        # Measure
        start = time.perf_counter()
        for _ in range(iterations):
            result = translator.parse_characteristic("2A6E", temp_data)
            assert result.parse_success
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Generous baseline to catch only severe regressions
        assert avg_time_ms < 10.0, (
            f"Temperature parsing excessively slow: {avg_time_ms:.4f}ms avg "
            f"(expected <10.0ms). Total: {elapsed:.4f}s for {iterations} iterations. "
            f"This indicates a major performance regression."
        )

    def test_batch_parse_performance(self, translator):
        """Track batch parsing performance (baseline: <20ms for 4 chars).

        This test ensures batch parsing remains efficient. Threshold is
        generous to accommodate different system speeds and CI environments.
        """
        sensor_data = {
            "2A19": bytes([0x55]),  # 85% battery
            "2A6E": bytes([0x58, 0x07]),  # 18.64°C temperature
            "2A6F": bytes([0x38, 0x19]),  # 65.12% humidity
            "2A6D": bytes([0x70, 0x96, 0x00, 0x00]),  # 996.8 hPa pressure
        }
        iterations = 500

        # Warmup
        for _ in range(10):
            translator.parse_characteristics(sensor_data)

        # Measure
        start = time.perf_counter()
        for _ in range(iterations):
            results = translator.parse_characteristics(sensor_data)
            assert len(results) == 4
            assert all(r.parse_success for r in results.values())
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Generous baseline to catch only severe regressions (20x slower than typical)
        assert avg_time_ms < 20.0, (
            f"Batch parsing excessively slow: {avg_time_ms:.4f}ms avg "
            f"(expected <20.0ms). Total: {elapsed:.4f}s for {iterations} iterations. "
            f"This indicates a major performance regression."
        )

    def test_uuid_resolution_performance(self, translator):
        """Track UUID resolution performance (baseline: <2ms).

        This test ensures characteristic info lookup remains fast.
        Threshold is generous to avoid system-dependent failures.
        """
        iterations = 1000

        # Warmup
        for _ in range(10):
            translator.get_characteristic_info("2A19")

        # Measure
        start = time.perf_counter()
        for _ in range(iterations):
            info = translator.get_characteristic_info("2A19")
            assert info is not None
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Generous baseline to catch only severe regressions (40x slower than typical)
        assert avg_time_ms < 2.0, (
            f"UUID resolution excessively slow: {avg_time_ms:.4f}ms avg "
            f"(expected <2.0ms). Total: {elapsed:.4f}s for {iterations} iterations. "
            f"This indicates a major performance regression."
        )

    def test_parse_timing_accuracy(self, translator):
        """Verify timing measurements are accurate and consistent.

        This test ensures the timing infrastructure itself is working correctly.
        Note: CI environments can have higher timing variability due to shared resources.
        """
        battery_data = bytes([0x64])
        iterations = 100

        # Extended warmup to ensure caches are fully populated
        for _ in range(100):
            translator.parse_characteristic("2A19", battery_data)

        # Measure multiple times to check consistency
        measurements = []
        for _ in range(7):  # Increased samples for better statistics
            start = time.perf_counter()
            for _ in range(iterations):
                translator.parse_characteristic("2A19", battery_data)
            elapsed = time.perf_counter() - start
            measurements.append(elapsed)

        # Discard first measurement (can be affected by remaining warmup effects)
        measurements = measurements[1:]

        # Check that measurements are consistent (coefficient of variation < 30%)
        # Increased threshold to accommodate CI environment variability
        avg_elapsed = sum(measurements) / len(measurements)
        std_dev = (sum((x - avg_elapsed) ** 2 for x in measurements) / len(measurements)) ** 0.5
        cv = (std_dev / avg_elapsed) * 100 if avg_elapsed > 0 else 0

        assert cv < 30, f"Timing measurements inconsistent: CV={cv:.1f}% (expected <30%). Measurements: {measurements}"

    def test_parse_with_logging_overhead(self, translator, caplog):
        """Track performance impact of logging.

        This test ensures logging overhead remains minimal when logs are captured
        (not printed to console, which is much slower).
        """
        import logging

        battery_data = bytes([0x64])
        iterations = 1000

        # Capture logs to avoid console I/O overhead
        caplog.set_level(logging.WARNING, logger="bluetooth_sig.core.translator")

        # Measure without logging (WARNING level)
        # Warmup
        for _ in range(10):
            translator.parse_characteristic("2A19", battery_data)

        start = time.perf_counter()
        for _ in range(iterations):
            translator.parse_characteristic("2A19", battery_data)
        time_without_logging = time.perf_counter() - start

        # Measure with DEBUG logging (captured, not printed)
        caplog.set_level(logging.DEBUG, logger="bluetooth_sig.core.translator")

        # Warmup
        for _ in range(10):
            translator.parse_characteristic("2A19", battery_data)

        start = time.perf_counter()
        for _ in range(iterations):
            translator.parse_characteristic("2A19", battery_data)
        time_with_logging = time.perf_counter() - start

        # Calculate overhead
        overhead_ratio = time_with_logging / time_without_logging
        overhead_pct = (overhead_ratio - 1) * 100

        # Logging overhead should be reasonable (less than 15x slower)
        # DEBUG logging creates 3 log records per parse with string formatting,
        # which adds significant overhead even when just capturing (not printing)
        # This threshold catches major regressions while being realistic
        assert overhead_ratio < 15.0, (
            f"Logging overhead too high: {overhead_pct:.1f}% "
            f"(expected <1400%). "
            f"Without: {time_without_logging:.4f}s, "
            f"With: {time_with_logging:.4f}s. "
            f"Note: This is in-memory logging overhead including string formatting."
        )

        # Verify logs were actually captured
        assert len(caplog.records) > 0, "No logs were captured"

        # Reset logging level
        caplog.set_level(logging.WARNING, logger="bluetooth_sig.core.translator")
