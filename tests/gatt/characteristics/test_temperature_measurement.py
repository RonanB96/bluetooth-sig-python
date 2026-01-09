"""Test temperature measurement characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics.temperature_measurement import (
    TemperatureMeasurementCharacteristic,
    TemperatureMeasurementData,
    TemperatureMeasurementFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types.units import TemperatureUnit

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperatureMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Temperature Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> TemperatureMeasurementCharacteristic:
        """Fixture providing a temperature measurement characteristic."""
        return TemperatureMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for temperature measurement characteristic."""
        return "2A1C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for temperature measurement characteristic covering various flag combinations."""
        return [
            # Test 1: Basic temperature measurement (Celsius, no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields, Celsius
                        0x20,
                        0x75,
                        0x38,
                        0x7B,  # temperature = 37.0°C (medfloat32)
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=37.0,
                    unit=TemperatureUnit.CELSIUS,
                    flags=TemperatureMeasurementFlags.CELSIUS_UNIT,
                    timestamp=None,
                    temperature_type=None,
                ),
                description="Basic temperature measurement (Celsius)",
            ),
            # Test 2: Fahrenheit temperature
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: Fahrenheit unit
                        0x90,
                        0x0B,
                        0x0F,
                        0x7C,  # temperature = 98.6°F (medfloat32)
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=98.6,
                    unit=TemperatureUnit.FAHRENHEIT,
                    flags=TemperatureMeasurementFlags.FAHRENHEIT_UNIT,
                    timestamp=None,
                    temperature_type=None,
                ),
                description="Fahrenheit temperature measurement",
            ),
            # Test 3: Temperature with timestamp
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: timestamp present
                        0x20,
                        0x75,
                        0x38,
                        0x7B,  # temperature = 37.0°C (medfloat32)
                        0xE7,
                        0x07,  # year = 2023
                        0x0C,  # month = 12
                        0x19,  # day = 25
                        0x0E,  # hour = 14
                        0x1E,  # minute = 30
                        0x2D,  # second = 45
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=37.0,
                    unit=TemperatureUnit.CELSIUS,
                    flags=TemperatureMeasurementFlags.TIMESTAMP_PRESENT,
                    timestamp=datetime.datetime(2023, 12, 25, 14, 30, 45),
                    temperature_type=None,
                ),
                description="Temperature measurement with timestamp",
            ),
            # Test 4: Temperature with type
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: temperature type present
                        0x20,
                        0x75,
                        0x38,
                        0x7B,  # temperature = 37.0°C (medfloat32)
                        0x01,  # temperature type = 1 (body)
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=37.0,
                    unit=TemperatureUnit.CELSIUS,
                    flags=TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT,
                    timestamp=None,
                    temperature_type=1,
                ),
                description="Temperature measurement with type",
            ),
            # Test 5: Full measurement with all optional fields (Fahrenheit)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x07,  # flags: Fahrenheit + timestamp + type (0x01 | 0x02 | 0x04)
                        0x90,
                        0x0B,
                        0x0F,
                        0x7C,  # temperature = 98.6°F (medfloat32)
                        0xE7,
                        0x07,  # year = 2023
                        0x0C,  # month = 12
                        0x19,  # day = 25
                        0x0E,  # hour = 14
                        0x1E,  # minute = 30
                        0x2D,  # second = 45
                        0x02,  # temperature type = 2 (ear)
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=98.6,
                    unit=TemperatureUnit.FAHRENHEIT,
                    flags=TemperatureMeasurementFlags.FAHRENHEIT_UNIT
                    | TemperatureMeasurementFlags.TIMESTAMP_PRESENT
                    | TemperatureMeasurementFlags.TEMPERATURE_TYPE_PRESENT,
                    timestamp=datetime.datetime(2023, 12, 25, 14, 30, 45),
                    temperature_type=2,
                ),
                description="Full Fahrenheit measurement with all optional fields",
            ),
            # Test 6: Different temperature value (fever)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: Celsius, no optional fields
                        0x80,
                        0xD0,
                        0x3B,
                        0x7B,  # temperature = 39.2°C (fever) (medfloat32)
                    ]
                ),
                expected_value=TemperatureMeasurementData(
                    temperature=39.2,
                    unit=TemperatureUnit.CELSIUS,
                    flags=TemperatureMeasurementFlags.CELSIUS_UNIT,
                    timestamp=None,
                    temperature_type=None,
                ),
                description="Fever temperature measurement",
            ),
        ]

    def test_temperature_measurement_invalid_data(self, characteristic: TemperatureMeasurementCharacteristic) -> None:
        """Test temperature measurement error handling."""
        # Too short data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x01]))
        assert "at least 5 bytes" in str(exc_info.value)

        # Missing temperature data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00]))
        assert "at least 5 bytes" in str(exc_info.value)
