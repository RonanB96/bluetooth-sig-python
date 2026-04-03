"""Tests for IntermediateCuffPressureCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.blood_pressure_common import (
    BloodPressureFlags,
    BloodPressureOptionalFields,
)
from bluetooth_sig.gatt.characteristics.blood_pressure_feature import BloodPressureFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure import (
    IntermediateCuffPressureCharacteristic,
    IntermediateCuffPressureData,
)
from bluetooth_sig.types.units import PressureUnit

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests, DependencyTestData


class TestIntermediateCuffPressureCharacteristic(CommonCharacteristicTests):
    """Test Intermediate Cuff Pressure characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> IntermediateCuffPressureCharacteristic:
        return IntermediateCuffPressureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A36"

    @pytest.fixture
    def dependency_test_data(self) -> list[DependencyTestData]:
        """Test data for optional Blood Pressure Feature dependency."""
        return [
            DependencyTestData(
                with_dependency_data={
                    str(IntermediateCuffPressureCharacteristic.get_class_uuid()): bytearray(
                        [
                            0x00,  # flags: mmHg unit, no optional fields
                            0x78,
                            0x80,  # current cuff pressure 120 mmHg (SFLOAT)
                            0xFF,
                            0x07,  # unused (NaN SFLOAT)
                            0xFF,
                            0x07,  # unused (NaN SFLOAT)
                        ]
                    ),
                    str(BloodPressureFeatureCharacteristic.get_class_uuid()): bytearray([0x01, 0x00]),
                },
                without_dependency_data=bytearray(
                    [
                        0x00,  # flags: mmHg unit, no optional fields
                        0x78,
                        0x80,  # current cuff pressure 120 mmHg (SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                    ]
                ),
                expected_with=IntermediateCuffPressureData(
                    current_cuff_pressure=120.0,
                    unit=PressureUnit.MMHG,
                    optional_fields=BloodPressureOptionalFields(),
                    flags=BloodPressureFlags(0),
                ),
                expected_without=IntermediateCuffPressureData(
                    current_cuff_pressure=120.0,
                    unit=PressureUnit.MMHG,
                    optional_fields=BloodPressureOptionalFields(),
                    flags=BloodPressureFlags(0),
                ),
                description="Cuff pressure with optional Blood Pressure Feature present",
            ),
        ]

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: mmHg unit, no optional fields
                        0x78,
                        0x80,  # current cuff pressure 120 mmHg (SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                    ]
                ),
                expected_value=IntermediateCuffPressureData(
                    current_cuff_pressure=120.0,
                    unit=PressureUnit.MMHG,
                    optional_fields=BloodPressureOptionalFields(),
                    flags=BloodPressureFlags(0),
                ),
                description="Basic 120 mmHg cuff pressure",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: kPa unit
                        0x10,
                        0x80,  # current cuff pressure 16.0 kPa (SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                    ]
                ),
                expected_value=IntermediateCuffPressureData(
                    current_cuff_pressure=16.0,
                    unit=PressureUnit.KPA,
                    optional_fields=BloodPressureOptionalFields(),
                    flags=BloodPressureFlags.UNITS_KPA,
                ),
                description="16.0 kPa cuff pressure",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: pulse rate present
                        0x50,
                        0x80,  # current cuff pressure 80 mmHg (SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                        0xFF,
                        0x07,  # unused (NaN SFLOAT)
                        0x48,
                        0x80,  # pulse rate 72 bpm (SFLOAT)
                    ]
                ),
                expected_value=IntermediateCuffPressureData(
                    current_cuff_pressure=80.0,
                    unit=PressureUnit.MMHG,
                    optional_fields=BloodPressureOptionalFields(pulse_rate=72.0),
                    flags=BloodPressureFlags.PULSE_RATE_PRESENT,
                ),
                description="80 mmHg cuff pressure with pulse rate 72 bpm",
            ),
        ]
