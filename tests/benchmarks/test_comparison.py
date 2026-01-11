"""Compare library parsing vs manual parsing."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator


@pytest.mark.benchmark
class TestLibraryVsManual:
    """Compare library performance vs manual parsing."""

    @pytest.mark.benchmark
    def test_battery_level_manual(self, benchmark: Any, battery_level_data: bytearray) -> None:
        """Manual battery level parsing."""

        def manual_parse() -> int:
            data = battery_level_data
            if len(data) != 1:
                raise ValueError("Invalid length")
            value = int(data[0])
            if not 0 <= value <= 100:
                raise ValueError("Out of range")
            return value

        result = benchmark(manual_parse)
        assert result == 85

    def test_battery_level_library(
        self, benchmark: Any, translator: BluetoothSIGTranslator, battery_level_data: bytearray
    ) -> None:
        """Library battery level parsing."""
        result = benchmark(translator.parse_characteristic, "2A19", battery_level_data)
        assert result == 85

    def test_temperature_manual(self, benchmark: Any, temperature_data: bytearray) -> None:
        """Manual temperature parsing."""

        def manual_parse() -> float:
            data = temperature_data
            if len(data) != 2:
                raise ValueError("Invalid length")
            raw = int.from_bytes(data, byteorder="little", signed=True)
            return raw * 0.01

        result = benchmark(manual_parse)
        assert abs(result - 24.04) < 0.01

    def test_temperature_library(
        self, benchmark: Any, translator: BluetoothSIGTranslator, temperature_data: bytearray
    ) -> None:
        """Library temperature parsing."""
        result = benchmark(translator.parse_characteristic, "2A6E", temperature_data)
        assert abs(result - 24.04) < 0.01

    def test_humidity_manual(self, benchmark: Any, humidity_data: bytearray) -> None:
        """Manual humidity parsing."""

        def manual_parse() -> float | None:
            data = humidity_data
            if len(data) != 2:
                raise ValueError("Invalid length")
            raw = int.from_bytes(data, byteorder="little", signed=False)
            if raw == 0xFFFF:
                return None
            if raw > 10000:
                raise ValueError("Out of range")
            return raw * 0.01

        result = benchmark(manual_parse)
        assert abs(result - 49.22) < 0.01

    def test_humidity_library(
        self, benchmark: Any, translator: BluetoothSIGTranslator, humidity_data: bytearray
    ) -> None:
        """Library humidity parsing."""
        result = benchmark(translator.parse_characteristic, "2A6F", humidity_data)
        assert abs(result - 49.22) < 0.01


@pytest.mark.benchmark
class TestOverheadAnalysis:
    """Analyze overhead of library vs manual parsing."""

    def test_uuid_resolution_overhead(self, benchmark: Any, translator: BluetoothSIGTranslator) -> None:
        """Measure UUID resolution overhead."""

        def uuid_lookup() -> object:
            return translator.get_sig_info_by_uuid("2A19")

        result = benchmark(uuid_lookup)
        assert result is not None

    def test_validation_overhead(self, benchmark: Any, battery_level_data: bytearray) -> None:
        """Measure validation overhead."""

        def validate_data() -> int:
            data = battery_level_data
            # Length check
            if len(data) != 1:
                raise ValueError("Invalid length")
            # Range check
            value = int(data[0])
            if not 0 <= value <= 100:
                raise ValueError("Out of range")
            return value

        result = benchmark(validate_data)
        assert result == 85

    def test_struct_creation_overhead(self, benchmark: Any) -> None:
        """Measure overhead of creating result structures."""
        from bluetooth_sig.gatt.characteristics.heart_rate_measurement import (
            HeartRateData,
            HeartRateMeasurementFlags,
            SensorContactState,
        )

        def create_result() -> HeartRateData:
            return HeartRateData(
                heart_rate=85,
                sensor_contact=SensorContactState.NOT_SUPPORTED,
                energy_expended=None,
                rr_intervals=(),
                flags=HeartRateMeasurementFlags(0),
            )

        result = benchmark(create_result)
        assert result.heart_rate == 85
