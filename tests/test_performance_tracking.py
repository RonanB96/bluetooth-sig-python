"""Performance tracking tests to monitor parsing speed over time.

These tests establish baseline performance metrics and fail if performance
regresses significantly, helping catch performance regressions early.
"""

from __future__ import annotations

import time

import pytest

from bluetooth_sig import BluetoothSIGTranslator


class TestPerformanceTracking:
    """Track parsing performance to detect regressions."""

    @pytest.fixture
    def translator(self):
        """Create a translator instance for testing."""
        return BluetoothSIGTranslator()

    def test_battery_level_parse_performance(self, translator):
        """Track battery level parsing performance (baseline: <0.1ms).

        This test establishes a performance baseline. If it fails, parsing
        performance may have regressed significantly.
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

        # Performance baseline: should complete in less than 0.1ms on average
        # This is a reasonable threshold that allows for slower CI environments
        assert avg_time_ms < 0.1, (
            f"Battery level parsing too slow: {avg_time_ms:.4f}ms avg "
            f"(expected <0.1ms). Total: {elapsed:.4f}s for {iterations} iterations"
        )

    def test_temperature_parse_performance(self, translator):
        """Track temperature parsing performance (baseline: <0.2ms).

        This test establishes a performance baseline for moderate complexity
        characteristics.
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

        # Performance baseline: should complete in less than 0.2ms on average
        assert avg_time_ms < 0.2, (
            f"Temperature parsing too slow: {avg_time_ms:.4f}ms avg "
            f"(expected <0.2ms). Total: {elapsed:.4f}s for {iterations} iterations"
        )

    def test_batch_parse_performance(self, translator):
        """Track batch parsing performance (baseline: <0.5ms for 4 chars).

        This test ensures batch parsing remains efficient.
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

        # Performance baseline: should complete in less than 0.5ms on average
        assert avg_time_ms < 0.5, (
            f"Batch parsing too slow: {avg_time_ms:.4f}ms avg "
            f"(expected <0.5ms). Total: {elapsed:.4f}s for {iterations} iterations"
        )

    def test_uuid_resolution_performance(self, translator):
        """Track UUID resolution performance (baseline: <0.05ms).

        This test ensures characteristic info lookup remains fast.
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

        # Performance baseline: should complete in less than 0.05ms on average
        assert avg_time_ms < 0.05, (
            f"UUID resolution too slow: {avg_time_ms:.4f}ms avg "
            f"(expected <0.05ms). Total: {elapsed:.4f}s for {iterations} iterations"
        )

    def test_parse_timing_accuracy(self, translator):
        """Verify timing measurements are accurate and consistent.

        This test ensures the timing infrastructure itself is working correctly.
        """
        battery_data = bytes([0x64])
        iterations = 100

        # Measure multiple times to check consistency
        measurements = []
        for _ in range(5):
            start = time.perf_counter()
            for _ in range(iterations):
                translator.parse_characteristic("2A19", battery_data)
            elapsed = time.perf_counter() - start
            measurements.append(elapsed)

        # Check that measurements are consistent (coefficient of variation < 20%)
        avg_elapsed = sum(measurements) / len(measurements)
        std_dev = (
            sum((x - avg_elapsed) ** 2 for x in measurements) / len(measurements)
        ) ** 0.5
        cv = (std_dev / avg_elapsed) * 100 if avg_elapsed > 0 else 0

        assert cv < 20, (
            f"Timing measurements inconsistent: CV={cv:.1f}% "
            f"(expected <20%). Measurements: {measurements}"
        )

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
