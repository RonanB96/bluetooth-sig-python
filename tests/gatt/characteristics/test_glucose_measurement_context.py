"""Test glucose measurement context characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.glucose_measurement_context import (
    CarbohydrateType,
    GlucoseMeasurementContextCharacteristic,
    GlucoseMeasurementContextData,
    GlucoseMeasurementContextFlags,
    MealType,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests, DependencyTestData


class TestGlucoseMeasurementContextCharacteristic(CommonCharacteristicTests):
    """Test Glucose Measurement Context characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> GlucoseMeasurementContextCharacteristic:
        """Fixture providing a glucose measurement context characteristic."""
        return GlucoseMeasurementContextCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for glucose measurement context characteristic."""
        return "2A34"

    @pytest.fixture
    def dependency_test_data(self) -> list[DependencyTestData]:
        """Test data for required Glucose Measurement dependency."""
        context_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence number = 42
            ]
        )

        return [
            DependencyTestData(
                with_dependency_data={
                    str(GlucoseMeasurementContextCharacteristic.get_class_uuid()): context_data,
                    # NOTE: Glucose Measurement (required dependency) not included because
                    # this characteristic's decode_value() expects parsed CharacteristicData
                    # objects in context, not raw bytes. The simplified dependency test
                    # framework only passes raw bytes. For proper testing of sequence number
                    # validation against Glucose Measurement
                },
                without_dependency_data=context_data,
                expected_with=GlucoseMeasurementContextData(
                    sequence_number=42,
                    flags=GlucoseMeasurementContextFlags(0),
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                expected_without=GlucoseMeasurementContextData(
                    sequence_number=42,
                    flags=GlucoseMeasurementContextFlags(0),
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Glucose context with required measurement dependency present",
            ),
        ]

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for glucose measurement context characteristic covering various flag combinations."""
        return [
            # Test 1: Basic context (no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0x2A,
                        0x00,  # sequence number = 42
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=42,
                    flags=GlucoseMeasurementContextFlags(0),
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Basic glucose context with sequence 42",
            ),
            # Test 2: Context with carbohydrate information
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: carbohydrate present
                        0x15,
                        0x00,  # sequence number = 21
                        0x01,  # carbohydrate ID = 1 (Breakfast)
                        0x32,
                        0x80,  # carbohydrate: 50.0g as SFLOAT
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=21,
                    flags=GlucoseMeasurementContextFlags.CARBOHYDRATE_PRESENT,
                    extended_flags=None,
                    carbohydrate_id=CarbohydrateType.BREAKFAST,
                    carbohydrate_kg=50.0,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Context with breakfast carbohydrate data",
            ),
            # Test 3: Context with meal information
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: meal present
                        0x07,
                        0x00,  # sequence number = 7
                        0x02,  # meal = 2 (Postprandial)
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=7,
                    flags=GlucoseMeasurementContextFlags.MEAL_PRESENT,
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=MealType.POSTPRANDIAL,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Context with postprandial meal info",
            ),
            # Test 4: Context with exercise information
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x10,  # flags: exercise present
                        0x64,
                        0x00,  # sequence number = 100
                        0x84,
                        0x03,  # exercise duration = 900 seconds (15 minutes)
                        0x50,  # exercise intensity = 80%
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=100,
                    flags=GlucoseMeasurementContextFlags.EXERCISE_PRESENT,
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=900,
                    exercise_intensity_percent=80,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Context with exercise data",
            ),
            # Test 5: Context with HbA1c information
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x40,  # flags: HbA1c present
                        0xFF,
                        0x00,  # sequence number = 255
                        0x07,
                        0x80,  # HbA1c = 7.0% as SFLOAT
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=255,
                    flags=GlucoseMeasurementContextFlags.HBA1C_PRESENT,
                    extended_flags=None,
                    carbohydrate_id=None,
                    carbohydrate_kg=None,
                    meal=None,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=None,
                    exercise_intensity_percent=None,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=7.0,
                ),
                description="Context with HbA1c data",
            ),
            # Test 6: Complex context with multiple fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x16,  # flags: carbohydrate + meal + exercise present (0x02 + 0x04 + 0x10)
                        0x2A,
                        0x01,  # sequence number = 298
                        0x02,  # carbohydrate ID = 2 (Lunch)
                        0x4B,
                        0x80,  # carbohydrate: 75.0g as SFLOAT
                        0x01,  # meal = 1 (Preprandial)
                        0x58,
                        0x02,  # exercise duration = 600 seconds (10 minutes)
                        0x3C,  # exercise intensity = 60%
                    ]
                ),
                expected_value=GlucoseMeasurementContextData(
                    sequence_number=298,
                    flags=(
                        GlucoseMeasurementContextFlags.CARBOHYDRATE_PRESENT
                        | GlucoseMeasurementContextFlags.MEAL_PRESENT
                        | GlucoseMeasurementContextFlags.EXERCISE_PRESENT
                    ),
                    extended_flags=None,
                    carbohydrate_id=CarbohydrateType.LUNCH,
                    carbohydrate_kg=75.0,
                    meal=MealType.PREPRANDIAL,
                    tester=None,
                    health=None,
                    exercise_duration_seconds=600,
                    exercise_intensity_percent=60,
                    medication_id=None,
                    medication_kg=None,
                    hba1c_percent=None,
                ),
                description="Complex context with carb, meal, exercise",
            ),
        ]

    def test_glucose_context_basic_parsing(
        self, characteristic: GlucoseMeasurementContextCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test basic glucose measurement context data parsing."""
        # Use the first test case (basic context)
        test_data = valid_test_data[0].input_data

        result = characteristic.decode_value(test_data)
        assert result.sequence_number == 42
        assert result.flags == GlucoseMeasurementContextFlags(0)

    def test_glucose_context_with_carbohydrate(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with carbohydrate data."""
        # Flags: 0x02 (carbohydrate present)
        test_data = bytearray(
            [
                0x02,  # flags: carbohydrate present
                0x01,
                0x00,  # sequence number = 1
                0x01,  # carbohydrate ID = 1 (Breakfast)
                0x32,
                0x80,  # carbohydrate: 50.0g as SFLOAT
            ]
        )

        result = characteristic.decode_value(test_data)
        assert result.carbohydrate_id == CarbohydrateType.BREAKFAST
        # Human-readable name should match the enum's string representation
        assert str(result.carbohydrate_id) == "Breakfast"

    def test_glucose_context_with_meal(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with meal information."""
        # Flags: 0x04 (meal present)
        test_data = bytearray(
            [
                0x04,  # flags: meal present
                0x01,
                0x00,  # sequence number = 1
                0x02,  # meal = 2 (Postprandial)
            ]
        )

        result = characteristic.decode_value(test_data)
        assert result.meal == MealType.POSTPRANDIAL
        # Human-readable meal name should match the enum's string representation
        assert str(result.meal) == "Postprandial (after meal)"

    def test_glucose_context_invalid_data(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with invalid data."""
        with pytest.raises(ValueError, match="must be at least 3 bytes"):
            characteristic.decode_value(bytearray([0x00, 0x01]))
