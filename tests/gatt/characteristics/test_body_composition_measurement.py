"""Test body composition measurement characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics.body_composition_measurement import (
    BodyCompositionFlags,
    BodyCompositionMeasurementCharacteristic,
    BodyCompositionMeasurementData,
)
from bluetooth_sig.types.units import MeasurementSystem, WeightUnit

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBodyCompositionMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Body Composition Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> BodyCompositionMeasurementCharacteristic:
        """Fixture providing a body composition measurement characteristic."""
        return BodyCompositionMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for body composition measurement characteristic."""
        return "2A9C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for body composition measurement characteristic covering various flag combinations."""
        return [
            # Test 1: Basic measurement (metric units, no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,
                        0x00,  # flags: no optional fields, metric units
                        0x32,
                        0x00,  # body fat percentage = 5.0% (50 * 0.1)
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=5.0,
                    flags=BodyCompositionFlags(0),
                    measurement_units=MeasurementSystem.METRIC,
                    timestamp=None,
                    user_id=None,
                    basal_metabolism=None,
                    muscle_mass=None,
                    muscle_mass_unit=None,
                    muscle_percentage=None,
                    fat_free_mass=None,
                    soft_lean_mass=None,
                    body_water_mass=None,
                    impedance=None,
                    weight=None,
                    height=None,
                ),
                description="Basic 5.0% body fat metric measurement",
            ),
            # Test 2: Imperial units with timestamp
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,
                        0x00,  # flags: imperial units + timestamp present
                        0x96,
                        0x00,  # body fat percentage = 15.0% (150 * 0.1)
                        0xE8,
                        0x07,
                        0x06,
                        0x14,
                        0x0A,
                        0x1E,
                        0x00,  # timestamp: 2024-06-20 10:30:00
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=15.0,
                    flags=BodyCompositionFlags.IMPERIAL_UNITS | BodyCompositionFlags.TIMESTAMP_PRESENT,
                    measurement_units=MeasurementSystem.IMPERIAL,
                    timestamp=datetime.datetime(2024, 6, 20, 10, 30, 0),
                    user_id=None,
                    basal_metabolism=None,
                    muscle_mass=None,
                    muscle_mass_unit=None,
                    muscle_percentage=None,
                    fat_free_mass=None,
                    soft_lean_mass=None,
                    body_water_mass=None,
                    impedance=None,
                    weight=None,
                    height=None,
                ),
                description="15.0% body fat imperial with timestamp",
            ),
            # Test 3: With user ID and basal metabolism
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0C,
                        0x00,  # flags: user ID + basal metabolism present
                        0x78,
                        0x00,  # body fat percentage = 12.0% (120 * 0.1)
                        0x05,  # user ID = 5
                        0x40,
                        0x06,  # basal metabolism = 1600 kJ
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=12.0,
                    flags=BodyCompositionFlags.USER_ID_PRESENT | BodyCompositionFlags.BASAL_METABOLISM_PRESENT,
                    measurement_units=MeasurementSystem.METRIC,
                    timestamp=None,
                    user_id=5,
                    basal_metabolism=1600,
                    muscle_mass=None,
                    muscle_mass_unit=None,
                    muscle_percentage=None,
                    fat_free_mass=None,
                    soft_lean_mass=None,
                    body_water_mass=None,
                    impedance=None,
                    weight=None,
                    height=None,
                ),
                description="12.0% body fat with user ID and metabolism",
            ),
            # Test 4: With muscle mass and percentage
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x30,
                        0x00,  # flags: muscle mass + muscle percentage present
                        0x64,
                        0x00,  # body fat percentage = 10.0% (100 * 0.1)
                        0xB8,
                        0x0B,  # muscle mass = 15.0 kg (3000 * 0.005) metric
                        0xC8,
                        0x00,  # muscle percentage = 20.0% (200 * 0.1)
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=10.0,
                    flags=BodyCompositionFlags.MUSCLE_MASS_PRESENT | BodyCompositionFlags.MUSCLE_PERCENTAGE_PRESENT,
                    measurement_units=MeasurementSystem.METRIC,
                    timestamp=None,
                    user_id=None,
                    basal_metabolism=None,
                    muscle_mass=15.0,  # 3000 * 0.005 kg
                    muscle_mass_unit=WeightUnit.KG,
                    muscle_percentage=20.0,
                    fat_free_mass=None,
                    soft_lean_mass=None,
                    body_water_mass=None,
                    impedance=None,
                    weight=None,
                    height=None,
                ),
                description="10.0% body fat with muscle mass and percentage",
            ),
            # Test 5: Complex measurement with multiple mass fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xC0,
                        0x01,  # flags: fat-free mass + soft lean mass + body water mass present
                        0x50,
                        0x00,  # body fat percentage = 8.0% (80 * 0.1)
                        0xE0,
                        0x2E,  # fat-free mass = 60.0 kg (12000 * 0.005) metric
                        0x10,
                        0x27,  # soft lean mass = 50.0 kg (10000 * 0.005) metric
                        0x40,
                        0x1F,  # body water mass = 40.0 kg (8000 * 0.005) metric
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=8.0,
                    flags=(
                        BodyCompositionFlags.FAT_FREE_MASS_PRESENT
                        | BodyCompositionFlags.SOFT_LEAN_MASS_PRESENT
                        | BodyCompositionFlags.BODY_WATER_MASS_PRESENT
                    ),
                    measurement_units=MeasurementSystem.METRIC,
                    timestamp=None,
                    user_id=None,
                    basal_metabolism=None,
                    muscle_mass=None,
                    muscle_mass_unit=None,
                    muscle_percentage=None,
                    fat_free_mass=60.0,  # 12000 * 0.005 kg
                    soft_lean_mass=50.0,  # 10000 * 0.005 kg
                    body_water_mass=40.0,  # 8000 * 0.005 kg
                    impedance=None,
                    weight=None,
                    height=None,
                ),
                description="Complex measurement with multiple mass fields",
            ),
            # Test 6: Full measurement with impedance, weight, and height
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,
                        0x0E,  # flags: impedance + weight + height present
                        0x46,
                        0x00,  # body fat percentage = 7.0% (70 * 0.1)
                        0x40,
                        0x1F,  # impedance = 800 ohms (8000 * 0.1)
                        0xB0,
                        0x36,  # weight = 70.0 kg (14000 * 0.005) metric
                        0xE8,
                        0x03,  # height = 1.0 m (1000 * 0.001) metric
                    ]
                ),
                expected_value=BodyCompositionMeasurementData(
                    body_fat_percentage=7.0,
                    flags=(
                        BodyCompositionFlags.IMPEDANCE_PRESENT
                        | BodyCompositionFlags.WEIGHT_PRESENT
                        | BodyCompositionFlags.HEIGHT_PRESENT
                    ),
                    measurement_units=MeasurementSystem.METRIC,
                    timestamp=None,
                    user_id=None,
                    basal_metabolism=None,
                    muscle_mass=None,
                    muscle_mass_unit=None,
                    muscle_percentage=None,
                    fat_free_mass=None,
                    soft_lean_mass=None,
                    body_water_mass=None,
                    impedance=800.0,
                    weight=70.0,  # 14000 * 0.005 kg
                    height=1.0,  # 10000 * 0.0001 m
                ),
                description="Full measurement with impedance, weight, height",
            ),
        ]

    def test_body_composition_basic_parsing(
        self, characteristic: BodyCompositionMeasurementCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test basic body composition measurement data parsing."""
        # Use the first test case (basic measurement)
        test_data = valid_test_data[0].input_data

        result = characteristic.parse_value(test_data)
        assert result.value is not None
        assert result.value.body_fat_percentage == 5.0
        assert result.value.measurement_units == MeasurementSystem.METRIC
        assert result.value.muscle_mass is None
        assert result.value.impedance is None

    def test_body_composition_with_muscle_data(self, characteristic: BodyCompositionMeasurementCharacteristic) -> None:
        """Test body composition with muscle mass and percentage."""
        # Flags: muscle mass + muscle percentage present
        test_data = bytearray(
            [
                0x30,
                0x00,  # flags: muscle mass + muscle percentage
                0x64,
                0x00,  # body fat percentage = 10.0%
                0x70,
                0x17,  # muscle mass = 30.0 kg (6000 * 0.005)
                0x96,
                0x00,  # muscle percentage = 15.0%
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result.value is not None
        assert result.value.muscle_mass == 30.0
        assert result.value.muscle_percentage == 15.0
        assert result.value.muscle_mass_unit == WeightUnit.KG

    def test_body_composition_imperial_units(self, characteristic: BodyCompositionMeasurementCharacteristic) -> None:
        """Test body composition with imperial units."""
        # Flags: imperial units
        test_data = bytearray(
            [
                0x01,
                0x00,  # flags: imperial units
                0x78,
                0x00,  # body fat percentage = 12.0%
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result.value is not None
        assert result.value.measurement_units == MeasurementSystem.IMPERIAL
        assert result.value.body_fat_percentage == 12.0

    def test_body_composition_invalid_data(self, characteristic: BodyCompositionMeasurementCharacteristic) -> None:
        """Test body composition with invalid data."""
        # Too short data - parse_value returns parse_success=False
        result = characteristic.parse_value(bytearray([0x00, 0x01]))
        assert result.parse_success is False
        assert result.error_message == (
            "Length validation failed for Body Composition Measurement: expected at least 4 bytes, got 2 "
            "(class-level constraint for BodyCompositionMeasurementCharacteristic)"
        )
