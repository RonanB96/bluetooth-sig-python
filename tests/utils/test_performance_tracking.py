"""Performance tracking tests using pytest-benchmark for historical comparison.

These tests use pytest-benchmark to track parsing performance over time.
Run with: pytest tests/test_performance_tracking.py --benchmark-only --benchmark-save=<name>
Compare with: pytest-benchmark compare <baseline> <current>

Historical data is stored in .benchmarks/ directory for regression detection.
"""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig import BluetoothSIGTranslator

# Skip all tests in this file until proper performance tracking is implemented
pytestmark = pytest.mark.skip(
    reason="Performance tracking disabled - needs proper benchmark infrastructure with historical data storage"
)


class TestPerformanceTracking:
    """Track parsing performance to detect regressions using pytest-benchmark."""

    @pytest.fixture
    def translator(self) -> BluetoothSIGTranslator:
        """Create a translator instance for testing."""
        return BluetoothSIGTranslator()

    @pytest.mark.benchmark
    def test_battery_level_parse_performance(
        self, translator: BluetoothSIGTranslator, benchmark: Any
    ) -> None:  # pytest-benchmark fixture
        """Benchmark battery level parsing performance."""
        battery_data = bytes([0x64])  # 100%

        def parse_battery() -> None:
            result = translator.parse_characteristic("2A19", battery_data)
            assert result.parse_success

        benchmark(parse_battery)

    @pytest.mark.benchmark
    def test_temperature_parse_performance(
        self, translator: BluetoothSIGTranslator, benchmark: Any
    ) -> None:  # pytest-benchmark fixture
        """Benchmark temperature parsing performance."""
        temp_data = bytes([0x64, 0x09])  # 24.20°C

        def parse_temperature() -> None:
            result = translator.parse_characteristic("2A6E", temp_data)
            assert result.parse_success

        benchmark(parse_temperature)

    @pytest.mark.benchmark
    def test_batch_parse_performance(
        self, translator: BluetoothSIGTranslator, benchmark: Any
    ) -> None:  # pytest-benchmark fixture
        """Benchmark batch parsing performance for multiple characteristics."""
        sensor_data = {
            "2A19": bytes([0x55]),  # 85% battery
            "2A6E": bytes([0x58, 0x07]),  # 18.64°C temperature
            "2A6F": bytes([0x38, 0x19]),  # 65.12% humidity
            "2A6D": bytes([0x70, 0x96, 0x00, 0x00]),  # 996.8 hPa pressure
        }

        def parse_batch() -> None:
            results = translator.parse_characteristics(sensor_data)
            assert len(results) == 4
            assert all(r.parse_success for r in results.values())

        benchmark(parse_batch)

    @pytest.mark.benchmark
    def test_uuid_resolution_performance(
        self, translator: BluetoothSIGTranslator, benchmark: Any
    ) -> None:  # pytest-benchmark fixture
        """Benchmark UUID resolution performance."""

        def resolve_uuid() -> None:
            info = translator.get_characteristic_info_by_uuid("2A19")
            assert info is not None

        benchmark(resolve_uuid)
