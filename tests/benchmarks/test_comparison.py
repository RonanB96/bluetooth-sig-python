"""Compare library parsing vs manual parsing."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.base import CharacteristicData


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
        assert result.value == 85

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
        assert abs(result.value - 24.04) < 0.01

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
        assert abs(result.value - 49.22) < 0.01


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
        # CharacteristicData is a gatt-level ParseResult that holds a `characteristic`
        # reference. Construct a minimal fake characteristic instance for the test.
        from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
        from bluetooth_sig.types.data_types import CharacteristicInfo

        class _FakeCharacteristic:
            properties: list[object]

            def __init__(self, info: CharacteristicInfo) -> None:
                self.info = info
                self.name = info.name
                self.uuid = info.uuid
                self.unit = info.unit
                self.properties = []

        from bluetooth_sig.types.gatt_enums import ValueType
        from bluetooth_sig.types.uuid import BluetoothUUID

        def create_result() -> CharacteristicData:
            info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),
                name="Battery Level",
                unit="%",
                value_type=ValueType.INT,
            )
            fake_char = _FakeCharacteristic(info)
            # Cast to BaseCharacteristic for type checker compatibility
            from typing import cast

            return CharacteristicData(
                characteristic=cast(BaseCharacteristic, fake_char),
                value=85,
                raw_data=bytes([85]),
                parse_success=True,
            )

        result = benchmark(create_result)
        assert result.value == 85
