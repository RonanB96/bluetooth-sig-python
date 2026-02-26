"""Tests for Enhanced Intermediate Cuff Pressure characteristic (0x2B35)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.blood_pressure_measurement import (
    BloodPressureMeasurementStatus,
)
from bluetooth_sig.gatt.characteristics.enhanced_blood_pressure_measurement import (
    EnhancedBloodPressureFlags,
    EpochYear,
)
from bluetooth_sig.gatt.characteristics.enhanced_intermediate_cuff_pressure import (
    EnhancedIntermediateCuffPressureCharacteristic,
    EnhancedIntermediateCuffPressureData,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from bluetooth_sig.types.units import PressureUnit
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


def _sfloat_bytes(value: float) -> list[int]:
    """Encode a float to SFLOAT and return as list of ints."""
    return list(IEEE11073Parser.encode_sfloat(value))


class TestEnhancedIntermediateCuffPressureCharacteristic(CommonCharacteristicTests):
    """Test Enhanced Intermediate Cuff Pressure characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return EnhancedIntermediateCuffPressureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2B35"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: mmHg, no optional fields
                        *_sfloat_bytes(150.0),  # cuff_pressure
                    ]
                ),
                expected_value=EnhancedIntermediateCuffPressureData(
                    flags=EnhancedBloodPressureFlags(0x00),
                    cuff_pressure=150.0,
                    unit=PressureUnit.MMHG,
                    epoch_year=EpochYear.EPOCH_1900,
                ),
                description="Minimal: cuff pressure only in mmHg",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: kPa
                        *_sfloat_bytes(20.0),  # cuff_pressure in kPa
                    ]
                ),
                expected_value=EnhancedIntermediateCuffPressureData(
                    flags=EnhancedBloodPressureFlags(0x01),
                    cuff_pressure=20.0,
                    unit=PressureUnit.KPA,
                    epoch_year=EpochYear.EPOCH_1900,
                ),
                description="kPa units",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x7E,  # flags: all optional present + epoch 2000
                        *_sfloat_bytes(130.0),  # cuff_pressure
                        0xE8,
                        0x03,
                        0x00,
                        0x00,  # timestamp: 1000
                        *_sfloat_bytes(72.0),  # pulse rate
                        0x01,  # user_id
                        0x05,
                        0x00,  # measurement_status
                        0xD0,
                        0x07,
                        0x00,
                        0x00,  # user_facing_time: 2000
                    ]
                ),
                expected_value=EnhancedIntermediateCuffPressureData(
                    flags=EnhancedBloodPressureFlags(0x7E),
                    cuff_pressure=130.0,
                    unit=PressureUnit.MMHG,
                    timestamp=1000,
                    pulse_rate=72.0,
                    user_id=1,
                    measurement_status=BloodPressureMeasurementStatus(0x0005),
                    user_facing_time=2000,
                    epoch_year=EpochYear.EPOCH_2000,
                ),
                description="All optional fields present, epoch 2000",
            ),
        ]

    def test_round_trip_all_fields(self) -> None:
        """Test encode/decode round-trip with all fields."""
        char = EnhancedIntermediateCuffPressureCharacteristic()
        original = EnhancedIntermediateCuffPressureData(
            flags=EnhancedBloodPressureFlags(0x7E),
            cuff_pressure=130.0,
            unit=PressureUnit.MMHG,
            timestamp=1000,
            pulse_rate=72.0,
            user_id=1,
            measurement_status=BloodPressureMeasurementStatus(0x0005),
            user_facing_time=2000,
            epoch_year=EpochYear.EPOCH_2000,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.cuff_pressure == original.cuff_pressure
        assert decoded.timestamp == original.timestamp
        assert decoded.pulse_rate == original.pulse_rate
        assert decoded.user_id == original.user_id
        assert decoded.measurement_status == original.measurement_status
        assert decoded.user_facing_time == original.user_facing_time
        assert decoded.epoch_year == original.epoch_year

    def test_round_trip_minimal(self) -> None:
        """Test encode/decode round-trip with minimal fields."""
        char = EnhancedIntermediateCuffPressureCharacteristic()
        original = EnhancedIntermediateCuffPressureData(
            flags=EnhancedBloodPressureFlags(0x00),
            cuff_pressure=150.0,
            unit=PressureUnit.MMHG,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.cuff_pressure == original.cuff_pressure
        assert decoded.timestamp is None
