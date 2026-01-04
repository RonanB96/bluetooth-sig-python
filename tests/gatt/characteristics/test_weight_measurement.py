"""Test weight measurement characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics.weight_measurement import (
    WeightMeasurementCharacteristic,
    WeightMeasurementData,
    WeightMeasurementFlags,
)
from bluetooth_sig.types.units import HeightUnit, MeasurementSystem, WeightUnit

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWeightMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Weight Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> WeightMeasurementCharacteristic:
        """Fixture providing a weight measurement characteristic."""
        return WeightMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for weight measurement characteristic."""
        return "2A9D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for weight measurement characteristic covering various flag combinations."""
        return [
            # Test 1: Basic weight measurement (metric units, no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0xB0,
                        0x36,  # weight = 70.0 kg (14000 * 0.005)
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=70.0,
                    weight_unit=WeightUnit.KG,
                    measurement_units=MeasurementSystem.METRIC,
                    flags=WeightMeasurementFlags(0x00),
                    timestamp=None,
                    user_id=None,
                    bmi=None,
                    height=None,
                    height_unit=None,
                ),
                description="Basic weight measurement (metric)",
            ),
            # Test 2: Imperial units
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: imperial units
                        0x54,
                        0x3D,  # weight = 157.00 lb (15700 * 0.01)
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=157.0,
                    weight_unit=WeightUnit.LB,
                    measurement_units=MeasurementSystem.IMPERIAL,
                    flags=WeightMeasurementFlags.IMPERIAL_UNITS,
                    timestamp=None,
                    user_id=None,
                    bmi=None,
                    height=None,
                    height_unit=None,
                ),
                description="Imperial units weight measurement",
            ),
            # Test 3: Weight with timestamp
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: timestamp present
                        0xB0,
                        0x36,  # weight = 70.0 kg (14000 * 0.005)
                        0xE7,
                        0x07,  # year = 2023
                        0x0C,  # month = 12
                        0x19,  # day = 25
                        0x0E,  # hour = 14
                        0x1E,  # minute = 30
                        0x2D,  # second = 45
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=70.0,
                    weight_unit=WeightUnit.KG,
                    measurement_units=MeasurementSystem.METRIC,
                    flags=WeightMeasurementFlags.TIMESTAMP_PRESENT,
                    timestamp=datetime.datetime(2023, 12, 25, 14, 30, 45),
                    user_id=None,
                    bmi=None,
                    height=None,
                    height_unit=None,
                ),
                description="Weight measurement with timestamp",
            ),
            # Test 4: Weight with user ID and BMI
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0C,  # flags: user ID + BMI present (0x04 | 0x08)
                        0xB0,
                        0x36,  # weight = 70.0 kg (14000 * 0.005)
                        0x05,  # user ID = 5
                        0xF5,
                        0x00,  # BMI = 24.5 (245 * 0.1)
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=70.0,
                    weight_unit=WeightUnit.KG,
                    measurement_units=MeasurementSystem.METRIC,
                    flags=WeightMeasurementFlags.USER_ID_PRESENT | WeightMeasurementFlags.BMI_PRESENT,
                    timestamp=None,
                    user_id=5,
                    bmi=24.5,
                    height=None,
                    height_unit=None,
                ),
                description="Weight measurement with user ID and BMI",
            ),
            # Test 5: Weight with height (metric)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x10,  # flags: height present
                        0xB0,
                        0x36,  # weight = 70.0 kg (14000 * 0.005)
                        0xD6,
                        0x06,  # height = 1.750 m (1750 * 0.001)
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=70.0,
                    weight_unit=WeightUnit.KG,
                    measurement_units=MeasurementSystem.METRIC,
                    flags=WeightMeasurementFlags.HEIGHT_PRESENT,
                    timestamp=None,
                    user_id=None,
                    bmi=None,
                    height=1.750,
                    height_unit=HeightUnit.METERS,
                ),
                description="Weight measurement with height (metric)",
            ),
            # Test 6: Full imperial measurement with all optional fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x1F,  # flags: all optional fields + imperial (0x01 | 0x02 | 0x04 | 0x08 | 0x10)
                        0x54,
                        0x3D,  # weight = 157.00 lb (15700 * 0.01)
                        0xE7,
                        0x07,  # year = 2023
                        0x0C,  # month = 12
                        0x19,  # day = 25
                        0x0E,  # hour = 14
                        0x1E,  # minute = 30
                        0x2D,  # second = 45
                        0x03,  # user ID = 3
                        0xF5,
                        0x00,  # BMI = 24.5 (245 * 0.1)
                        0xA8,
                        0x02,  # height = 68.0 inches (680 * 0.1)
                    ]
                ),
                expected_value=WeightMeasurementData(
                    weight=157.0,
                    weight_unit=WeightUnit.LB,
                    measurement_units=MeasurementSystem.IMPERIAL,
                    flags=(
                        WeightMeasurementFlags.IMPERIAL_UNITS
                        | WeightMeasurementFlags.TIMESTAMP_PRESENT
                        | WeightMeasurementFlags.USER_ID_PRESENT
                        | WeightMeasurementFlags.BMI_PRESENT
                        | WeightMeasurementFlags.HEIGHT_PRESENT
                    ),
                    timestamp=datetime.datetime(2023, 12, 25, 14, 30, 45),
                    user_id=3,
                    bmi=24.5,
                    height=68.0,
                    height_unit=HeightUnit.INCHES,
                ),
                description="Full imperial measurement with all optional fields",
            ),
        ]

    def test_weight_measurement_invalid_data(self, characteristic: WeightMeasurementCharacteristic) -> None:
        """Test weight measurement error handling."""
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        # Too short data - parse_value raises CharacteristicParseError
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x01]))
        assert "Length validation failed for Weight Measurement: expected at least 3 bytes, got 2" in str(
            exc_info.value
        )

        # Missing weight data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00]))
        assert "Length validation failed for Weight Measurement: expected at least 3 bytes, got 1" in str(
            exc_info.value
        )
