"""Compare library parsing vs manual parsing."""

from __future__ import annotations


class TestLibraryVsManual:
    """Compare library performance vs manual parsing."""

    def test_battery_level_manual(self, benchmark, battery_level_data):
        """Manual battery level parsing."""
        def manual_parse():
            data = battery_level_data
            if len(data) != 1:
                raise ValueError("Invalid length")
            value = int(data[0])
            if not 0 <= value <= 100:
                raise ValueError("Out of range")
            return value

        result = benchmark(manual_parse)
        assert result == 85

    def test_battery_level_library(self, benchmark, translator, battery_level_data):
        """Library battery level parsing."""
        result = benchmark(
            translator.parse_characteristic,
            "2A19",
            battery_level_data
        )
        assert result.value == 85

    def test_temperature_manual(self, benchmark, temperature_data):
        """Manual temperature parsing."""
        def manual_parse():
            data = temperature_data
            if len(data) != 2:
                raise ValueError("Invalid length")
            raw = int.from_bytes(data, byteorder='little', signed=True)
            return raw * 0.01

        result = benchmark(manual_parse)
        assert abs(result - 24.04) < 0.01

    def test_temperature_library(self, benchmark, translator, temperature_data):
        """Library temperature parsing."""
        result = benchmark(
            translator.parse_characteristic,
            "2A6E",
            temperature_data
        )
        assert abs(result.value - 24.04) < 0.01

    def test_humidity_manual(self, benchmark, humidity_data):
        """Manual humidity parsing."""
        def manual_parse():
            data = humidity_data
            if len(data) != 2:
                raise ValueError("Invalid length")
            raw = int.from_bytes(data, byteorder='little', signed=False)
            if raw == 0xFFFF:
                return None
            if raw > 10000:
                raise ValueError("Out of range")
            return raw * 0.01

        result = benchmark(manual_parse)
        assert abs(result - 49.22) < 0.01

    def test_humidity_library(self, benchmark, translator, humidity_data):
        """Library humidity parsing."""
        result = benchmark(
            translator.parse_characteristic,
            "2A6F",
            humidity_data
        )
        assert abs(result.value - 49.22) < 0.01


class TestOverheadAnalysis:
    """Analyze overhead of library vs manual parsing."""

    def test_uuid_resolution_overhead(self, benchmark, translator):
        """Measure UUID resolution overhead."""
        def uuid_lookup():
            return translator.get_sig_info_by_uuid("2A19")

        result = benchmark(uuid_lookup)
        assert result is not None

    def test_validation_overhead(self, benchmark, battery_level_data):
        """Measure validation overhead."""
        def validate_data():
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

    def test_struct_creation_overhead(self, benchmark):
        """Measure overhead of creating result structures."""
        from bluetooth_sig.types.data_types import CharacteristicData, CharacteristicInfo
        from bluetooth_sig.types.gatt_enums import ValueType
        from bluetooth_sig.types.uuid import BluetoothUUID

        def create_result():
            info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),
                name="Battery Level",
                description="",
                value_type=ValueType.INT,
                unit="%",
                properties=[]
            )
            return CharacteristicData(
                info=info,
                value=85,
                raw_data=bytearray([85]),
                parse_success=True
            )

        result = benchmark(create_result)
        assert result.value == 85
