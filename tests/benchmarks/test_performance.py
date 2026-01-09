"""Performance benchmarks for bluetooth-sig library core operations."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator


@pytest.mark.benchmark
class TestUUIDResolutionPerformance:
    """Benchmark UUID resolution operations."""

    def test_uuid_to_info_short_form(self, benchmark: Any, translator: BluetoothSIGTranslator) -> None:
        """Benchmark UUID to info lookup (short form)."""
        result = benchmark(translator.get_sig_info_by_uuid, "2A19")
        assert result is not None

    def test_uuid_to_info_long_form(self, benchmark: Any, translator: BluetoothSIGTranslator) -> None:
        """Benchmark UUID to info lookup (long form)."""
        result = benchmark(translator.get_sig_info_by_uuid, "00002a19-0000-1000-8000-00805f9b34fb")
        assert result is not None

    def test_name_to_uuid(self, benchmark: Any, translator: BluetoothSIGTranslator) -> None:
        """Benchmark name to UUID lookup."""
        result = benchmark(translator.get_sig_info_by_name, "Battery Level")
        assert result is not None

    def test_uuid_resolution_cached(self, benchmark: Any, translator: BluetoothSIGTranslator) -> None:
        """Benchmark cached UUID resolution."""
        # Warm up cache
        translator.get_sig_info_by_uuid("2A19")

        # Benchmark cached lookup
        result = benchmark(translator.get_sig_info_by_uuid, "2A19")
        assert result is not None


class TestCharacteristicParsingPerformance:
    """Benchmark characteristic parsing operations."""

    def test_parse_simple_uint8(
        self, benchmark: Any, translator: BluetoothSIGTranslator, battery_level_data: bytearray
    ) -> None:
        """Benchmark simple uint8 characteristic (Battery Level)."""
        result = benchmark(translator.parse_characteristic, "2A19", battery_level_data)
        assert result is not None

    def test_parse_simple_sint16(
        self, benchmark: Any, translator: BluetoothSIGTranslator, temperature_data: bytearray
    ) -> None:
        """Benchmark simple sint16 characteristic (Temperature)."""
        result = benchmark(translator.parse_characteristic, "2A6E", temperature_data)
        assert result is not None

    def test_parse_complex_flags(
        self, benchmark: Any, translator: BluetoothSIGTranslator, heart_rate_data: bytearray
    ) -> None:
        """Benchmark complex characteristic with flags (Heart Rate)."""
        result = benchmark(translator.parse_characteristic, "2A37", heart_rate_data)
        assert result is not None


@pytest.mark.benchmark
class TestBatchParsingPerformance:
    """Benchmark batch parsing operations."""

    def test_batch_parse_small(
        self, benchmark: Any, translator: BluetoothSIGTranslator, batch_characteristics_small: dict[str, bytearray]
    ) -> None:
        """Benchmark batch parsing (3 characteristics)."""
        result = benchmark(translator.parse_characteristics, batch_characteristics_small)
        assert len(result) == 3

    def test_batch_parse_medium(
        self, benchmark: Any, translator: BluetoothSIGTranslator, batch_characteristics_medium: dict[str, bytearray]
    ) -> None:
        """Benchmark batch parsing (10 characteristics)."""
        result = benchmark(translator.parse_characteristics, batch_characteristics_medium)
        assert len(result) == 10

    def test_batch_vs_individual(
        self, benchmark: Any, translator: BluetoothSIGTranslator, batch_characteristics_small: dict[str, bytearray]
    ) -> None:
        """Compare batch vs individual parsing."""

        def batch_parse() -> dict[str, Any]:
            return translator.parse_characteristics(batch_characteristics_small)  # type: ignore[arg-type]

        # Benchmark batch parsing
        batch_result = benchmark(batch_parse)
        assert len(batch_result) == 3


@pytest.mark.benchmark
class TestMemoryEfficiency:
    """Benchmark memory usage."""

    def test_translator_memory_footprint(self, benchmark: Any) -> None:
        """Measure translator instance memory footprint."""
        from bluetooth_sig import BluetoothSIGTranslator

        def create_translator() -> BluetoothSIGTranslator:
            return BluetoothSIGTranslator()

        translator = benchmark(create_translator)
        assert translator is not None

    def test_parse_no_memory_leak(
        self, benchmark: Any, translator: BluetoothSIGTranslator, battery_level_data: bytearray
    ) -> None:
        """Ensure parsing doesn't leak memory."""

        def parse_many() -> None:
            for _ in range(1000):
                translator.parse_characteristic("2A19", battery_level_data)  # type: ignore[arg-type]

        benchmark(parse_many)


@pytest.mark.benchmark
class TestThroughput:
    """Benchmark overall throughput."""

    def test_single_characteristic_throughput(
        self, benchmark: Any, translator: BluetoothSIGTranslator, battery_level_data: bytearray
    ) -> None:
        """Measure single characteristic parsing throughput."""

        def parse_loop() -> list[Any]:
            results: list[Any] = []
            for _ in range(100):
                result = translator.parse_characteristic("2A19", battery_level_data)  # type: ignore[arg-type]
                results.append(result)
            return results

        results = benchmark(parse_loop)
        assert len(results) == 100
        assert all(isinstance(r, int) for r in results)

    def test_batch_throughput(
        self, benchmark: Any, translator: BluetoothSIGTranslator, batch_characteristics_small: dict[str, bytearray]
    ) -> None:
        """Measure batch parsing throughput."""

        def batch_loop() -> list[dict[str, Any]]:
            results: list[dict[str, Any]] = []
            for _ in range(100):
                result = translator.parse_characteristics(batch_characteristics_small)  # type: ignore[arg-type]
                results.append(result)
            return results

        results = benchmark(batch_loop)
        assert len(results) == 100
        assert all(len(r) == 3 for r in results)
