"""Tests for Intermediate Temperature characteristic (0x2A1E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.intermediate_temperature import (
    IntermediateTemperatureCharacteristic,
    IntermediateTemperatureData,
    IntermediateTemperatureFlags,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from bluetooth_sig.types.units import TemperatureUnit
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIntermediateTemperatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Intermediate Temperature characteristic."""

    @pytest.fixture
    def characteristic(self) -> IntermediateTemperatureCharacteristic:
        """Return an Intermediate Temperature characteristic instance."""
        return IntermediateTemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Intermediate Temperature characteristic."""
        return "2A1E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for intermediate temperature."""
        # Celsius only (flags=0x00)
        temp_bytes_celsius = IEEE11073Parser.encode_float32(36.5)
        celsius_data = bytearray([0x00]) + temp_bytes_celsius
        celsius_expected = IntermediateTemperatureData(
            temperature=36.5,
            unit=TemperatureUnit.CELSIUS,
            flags=IntermediateTemperatureFlags(0x00),
        )

        # Fahrenheit encoding: flags=0x01
        temp_bytes_fahr = IEEE11073Parser.encode_float32(98.6)
        fahr_data = bytearray([0x01]) + temp_bytes_fahr
        fahr_expected = IntermediateTemperatureData(
            temperature=98.6,
            unit=TemperatureUnit.FAHRENHEIT,
            flags=IntermediateTemperatureFlags.FAHRENHEIT_UNIT,
        )

        return [
            CharacteristicTestData(
                input_data=bytearray(celsius_data),
                expected_value=celsius_expected,
                description="Celsius body temperature 36.5°C",
            ),
            CharacteristicTestData(
                input_data=bytearray(fahr_data),
                expected_value=fahr_expected,
                description="Fahrenheit body temperature 98.6°F",
            ),
        ]

    def test_celsius_decode(self) -> None:
        """Test decoding a Celsius temperature."""
        char = IntermediateTemperatureCharacteristic()
        temp_bytes = IEEE11073Parser.encode_float32(36.5)
        data = bytearray([0x00]) + temp_bytes
        result = char.parse_value(data)
        assert result.temperature == pytest.approx(36.5, abs=0.1)
        assert result.unit == TemperatureUnit.CELSIUS

    def test_fahrenheit_decode(self) -> None:
        """Test decoding a Fahrenheit temperature."""
        char = IntermediateTemperatureCharacteristic()
        temp_bytes = IEEE11073Parser.encode_float32(98.6)
        data = bytearray([0x01]) + temp_bytes
        result = char.parse_value(data)
        assert result.temperature == pytest.approx(98.6, abs=0.1)
        assert result.unit == TemperatureUnit.FAHRENHEIT

    def test_with_timestamp(self) -> None:
        """Test decoding with optional timestamp present."""
        from datetime import datetime

        char = IntermediateTemperatureCharacteristic()
        temp_bytes = IEEE11073Parser.encode_float32(37.0)
        ts_bytes = IEEE11073Parser.encode_timestamp(datetime(2024, 3, 10, 14, 30, 0))
        data = bytearray([0x02]) + temp_bytes + ts_bytes
        result = char.parse_value(data)
        assert result.temperature == pytest.approx(37.0, abs=0.1)
        assert result.timestamp == datetime(2024, 3, 10, 14, 30, 0)
