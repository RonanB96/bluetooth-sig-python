"""Tests for Enhanced Blood Pressure Measurement characteristic (0x2B34)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.blood_pressure_measurement import (
    BloodPressureMeasurementStatus,
)
from bluetooth_sig.gatt.characteristics.enhanced_blood_pressure_measurement import (
    EnhancedBloodPressureData,
    EnhancedBloodPressureFlags,
    EnhancedBloodPressureMeasurementCharacteristic,
    EpochYear,
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


class TestEnhancedBloodPressureMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Enhanced Blood Pressure Measurement characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return EnhancedBloodPressureMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2B34"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Enhanced Blood Pressure Measurement."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: mmHg, no optional fields, epoch 1900
                        *_sfloat_bytes(120.0),  # systolic
                        *_sfloat_bytes(80.0),  # diastolic
                        *_sfloat_bytes(100.0),  # MAP
                    ]
                ),
                expected_value=EnhancedBloodPressureData(
                    flags=EnhancedBloodPressureFlags(0x00),
                    systolic=120.0,
                    diastolic=80.0,
                    mean_arterial_pressure=100.0,
                    unit=PressureUnit.MMHG,
                    epoch_year=EpochYear.EPOCH_1900,
                ),
                description="Minimal: mmHg, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: kPa
                        *_sfloat_bytes(16.0),  # systolic kPa
                        *_sfloat_bytes(11.0),  # diastolic kPa
                        *_sfloat_bytes(13.0),  # MAP kPa
                    ]
                ),
                expected_value=EnhancedBloodPressureData(
                    flags=EnhancedBloodPressureFlags(0x01),
                    systolic=16.0,
                    diastolic=11.0,
                    mean_arterial_pressure=13.0,
                    unit=PressureUnit.KPA,
                    epoch_year=EpochYear.EPOCH_1900,
                ),
                description="kPa units, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x7E,  # flags: all optional present + epoch 2000
                        *_sfloat_bytes(120.0),
                        *_sfloat_bytes(80.0),
                        *_sfloat_bytes(100.0),
                        0x80,
                        0x51,
                        0x01,
                        0x00,  # timestamp: 86400 seconds
                        *_sfloat_bytes(72.0),  # pulse rate
                        0x05,  # user_id
                        0x03,
                        0x00,  # measurement_status: 0x0003
                        0x00,
                        0xA3,
                        0x02,
                        0x00,  # user_facing_time: 172800
                    ]
                ),
                expected_value=EnhancedBloodPressureData(
                    flags=EnhancedBloodPressureFlags(0x7E),
                    systolic=120.0,
                    diastolic=80.0,
                    mean_arterial_pressure=100.0,
                    unit=PressureUnit.MMHG,
                    timestamp=86400,
                    pulse_rate=72.0,
                    user_id=5,
                    measurement_status=BloodPressureMeasurementStatus(0x0003),
                    user_facing_time=172800,
                    epoch_year=EpochYear.EPOCH_2000,
                ),
                description="All optional fields present, epoch 2000",
            ),
        ]

    def test_timestamp_only(self) -> None:
        """Test with only timestamp present."""
        char = EnhancedBloodPressureMeasurementCharacteristic()
        data = bytearray(
            [
                0x02,  # flags: timestamp present
                *_sfloat_bytes(120.0),
                *_sfloat_bytes(80.0),
                *_sfloat_bytes(100.0),
                0xE8,
                0x03,
                0x00,
                0x00,  # timestamp: 1000
            ]
        )
        result = char.parse_value(data)
        assert result.timestamp == 1000
        assert result.pulse_rate is None
        assert result.user_facing_time is None

    def test_user_facing_time_only(self) -> None:
        """Test with only user facing time present."""
        char = EnhancedBloodPressureMeasurementCharacteristic()
        data = bytearray(
            [
                0x20,  # flags: user facing time present
                *_sfloat_bytes(120.0),
                *_sfloat_bytes(80.0),
                *_sfloat_bytes(100.0),
                0xD0,
                0x07,
                0x00,
                0x00,  # user_facing_time: 2000
            ]
        )
        result = char.parse_value(data)
        assert result.timestamp is None
        assert result.user_facing_time == 2000

    def test_epoch_flag(self) -> None:
        """Test epoch start flag interpretation."""
        char = EnhancedBloodPressureMeasurementCharacteristic()
        # Epoch 1900
        data_1900 = bytearray([0x00, *_sfloat_bytes(120.0), *_sfloat_bytes(80.0), *_sfloat_bytes(100.0)])
        assert char.parse_value(data_1900).epoch_year == EpochYear.EPOCH_1900

        # Epoch 2000
        data_2000 = bytearray([0x40, *_sfloat_bytes(120.0), *_sfloat_bytes(80.0), *_sfloat_bytes(100.0)])
        assert char.parse_value(data_2000).epoch_year == EpochYear.EPOCH_2000

    def test_round_trip_all_fields(self) -> None:
        """Test encode/decode round-trip with all fields."""
        char = EnhancedBloodPressureMeasurementCharacteristic()
        original = EnhancedBloodPressureData(
            flags=EnhancedBloodPressureFlags(0x7E),
            systolic=120.0,
            diastolic=80.0,
            mean_arterial_pressure=100.0,
            unit=PressureUnit.MMHG,
            timestamp=86400,
            pulse_rate=72.0,
            user_id=5,
            measurement_status=BloodPressureMeasurementStatus(0x0003),
            user_facing_time=172800,
            epoch_year=EpochYear.EPOCH_2000,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.systolic == original.systolic
        assert decoded.diastolic == original.diastolic
        assert decoded.mean_arterial_pressure == original.mean_arterial_pressure
        assert decoded.unit == original.unit
        assert decoded.timestamp == original.timestamp
        assert decoded.pulse_rate == original.pulse_rate
        assert decoded.user_id == original.user_id
        assert decoded.measurement_status == original.measurement_status
        assert decoded.user_facing_time == original.user_facing_time
        assert decoded.epoch_year == original.epoch_year

    def test_round_trip_minimal(self) -> None:
        """Test encode/decode round-trip with minimal fields."""
        char = EnhancedBloodPressureMeasurementCharacteristic()
        original = EnhancedBloodPressureData(
            flags=EnhancedBloodPressureFlags(0x00),
            systolic=120.0,
            diastolic=80.0,
            mean_arterial_pressure=100.0,
            unit=PressureUnit.MMHG,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.systolic == original.systolic
        assert decoded.unit == original.unit
        assert decoded.timestamp is None
