"""Test blood pressure measurement characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics.blood_pressure_measurement import (
    BloodPressureData,
    BloodPressureFlags,
    BloodPressureMeasurementCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBloodPressureMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Blood Pressure Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> BloodPressureMeasurementCharacteristic:
        """Fixture providing a blood pressure measurement characteristic."""
        return BloodPressureMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for blood pressure measurement characteristic."""
        return "2A35"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for blood pressure measurement covering various flag combinations."""
        return [
            # Test 1: Basic measurement (mmHg, no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: mmHg unit, no optional fields
                        0x78,
                        0x00,  # systolic 120 mmHg as SFLOAT
                        0x50,
                        0x00,  # diastolic 80 mmHg as SFLOAT
                        0x5A,
                        0x00,  # mean arterial pressure 90 mmHg as SFLOAT
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=120.0,
                    diastolic=80.0,
                    mean_arterial_pressure=90.0,
                    unit="mmHg",
                    flags=0,
                    timestamp=None,
                    pulse_rate=None,
                    user_id=None,
                    measurement_status=None,
                ),
                description="Basic 120/80 mmHg measurement",
            ),
            # Test 2: kPa unit measurement
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: kPa unit
                        0x10,
                        0x00,  # systolic 16.0 kPa as SFLOAT
                        0x0B,
                        0x00,  # diastolic 11.0 kPa as SFLOAT
                        0x0C,
                        0x00,  # mean arterial pressure 12.0 kPa as SFLOAT
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=16.0,
                    diastolic=11.0,
                    mean_arterial_pressure=12.0,
                    unit="kPa",
                    flags=BloodPressureFlags.UNITS_KPA,
                    timestamp=None,
                    pulse_rate=None,
                    user_id=None,
                    measurement_status=None,
                ),
                description="16.0/11.0 kPa measurement",
            ),
            # Test 3: With timestamp
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: timestamp present
                        0x8C,
                        0x00,  # systolic 140 mmHg as SFLOAT
                        0x5A,
                        0x00,  # diastolic 90 mmHg as SFLOAT
                        0x6E,
                        0x00,  # mean arterial pressure 110 mmHg as SFLOAT
                        0xE8,
                        0x07,
                        0x03,
                        0x0F,
                        0x0E,
                        0x1E,
                        0x2D,  # timestamp: 2024-03-15 14:30:45
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=140.0,
                    diastolic=90.0,
                    mean_arterial_pressure=110.0,
                    unit="mmHg",
                    flags=BloodPressureFlags.TIMESTAMP_PRESENT,
                    timestamp=datetime.datetime(2024, 3, 15, 14, 30, 45),
                    pulse_rate=None,
                    user_id=None,
                    measurement_status=None,
                ),
                description="140/90 mmHg with timestamp",
            ),
            # Test 4: With pulse rate
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: pulse rate present
                        0x78,
                        0x00,  # systolic 120 mmHg as SFLOAT
                        0x50,
                        0x00,  # diastolic 80 mmHg as SFLOAT
                        0x5A,
                        0x00,  # mean arterial pressure 90 mmHg as SFLOAT
                        0x48,
                        0x00,  # pulse rate 72 bpm as SFLOAT
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=120.0,
                    diastolic=80.0,
                    mean_arterial_pressure=90.0,
                    unit="mmHg",
                    flags=BloodPressureFlags.PULSE_RATE_PRESENT,
                    timestamp=None,
                    pulse_rate=72.0,
                    user_id=None,
                    measurement_status=None,
                ),
                description="120/80 mmHg with 72 bpm pulse",
            ),
            # Test 5: With user ID and measurement status
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x18,  # flags: user ID + measurement status present
                        0x78,
                        0x00,  # systolic 120 mmHg as SFLOAT
                        0x50,
                        0x00,  # diastolic 80 mmHg as SFLOAT
                        0x5A,
                        0x00,  # mean arterial pressure 90 mmHg as SFLOAT
                        0x05,  # user ID = 5
                        0x03,
                        0x00,  # measurement status: body movement + cuff loose
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=120.0,
                    diastolic=80.0,
                    mean_arterial_pressure=90.0,
                    unit="mmHg",
                    flags=BloodPressureFlags.USER_ID_PRESENT | BloodPressureFlags.MEASUREMENT_STATUS_PRESENT,
                    timestamp=None,
                    pulse_rate=None,
                    user_id=5,
                    measurement_status=3,  # Body movement + cuff loose
                ),
                description="120/80 mmHg with user ID and status flags",
            ),
            # Test 6: Complex measurement with all optional fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x1F,  # flags: all fields present + kPa unit
                        0x12,
                        0x00,  # systolic 18.0 kPa as SFLOAT
                        0x0C,
                        0x00,  # diastolic 12.0 kPa as SFLOAT
                        0x0E,
                        0x00,  # mean arterial pressure 14.0 kPa as SFLOAT
                        0xE8,
                        0x07,
                        0x06,
                        0x14,
                        0x10,
                        0x2D,
                        0x0A,  # timestamp: 2024-06-20 16:45:10
                        0x54,
                        0x00,  # pulse rate 84 bpm as SFLOAT
                        0x03,  # user ID = 3
                        0x1C,
                        0x00,  # measurement status: irregular pulse + rate out of range + improper position
                    ]
                ),
                expected_value=BloodPressureData(
                    systolic=18.0,
                    diastolic=12.0,
                    mean_arterial_pressure=14.0,
                    unit="kPa",
                    flags=(
                        BloodPressureFlags.UNITS_KPA
                        | BloodPressureFlags.TIMESTAMP_PRESENT
                        | BloodPressureFlags.PULSE_RATE_PRESENT
                        | BloodPressureFlags.USER_ID_PRESENT
                        | BloodPressureFlags.MEASUREMENT_STATUS_PRESENT
                    ),
                    timestamp=datetime.datetime(2024, 6, 20, 16, 45, 10),
                    pulse_rate=84.0,
                    user_id=3,
                    measurement_status=28,  # Multiple status flags
                ),
                description="Complex 18.0/12.0 kPa measurement with all fields",
            ),
        ]

    def test_blood_pressure_measurement_basic_parsing(
        self, characteristic: BloodPressureMeasurementCharacteristic
    ) -> None:
        """Test basic blood pressure measurement parsing."""
        # Basic 120/80 mmHg
        test_data = bytearray(
            [
                0x00,  # flags: mmHg, no optional fields
                0x78,
                0x00,  # systolic 120
                0x50,
                0x00,  # diastolic 80
                0x5A,
                0x00,  # MAP 90
            ]
        )

        result: BloodPressureData = characteristic.decode_value(test_data)
        assert result.systolic == 120.0
        assert result.diastolic == 80.0
        assert result.mean_arterial_pressure == 90.0
        assert result.unit == "mmHg"
        assert result.timestamp is None
        assert result.pulse_rate is None

    def test_blood_pressure_with_all_fields(self, characteristic: BloodPressureMeasurementCharacteristic) -> None:
        """Test blood pressure measurement with all optional fields."""
        # All fields present
        test_data = bytearray(
            [
                0x1E,  # flags: timestamp + pulse + user + status (no kPa)
                0x78,
                0x00,  # systolic 120
                0x50,
                0x00,  # diastolic 80
                0x5A,
                0x00,  # MAP 90
                0xE8,
                0x07,
                0x03,
                0x0F,
                0x0E,
                0x1E,
                0x2D,  # timestamp
                0x48,
                0x00,  # pulse rate 72
                0x01,  # user ID 1
                0x01,
                0x00,  # status: body movement
            ]
        )

        result: BloodPressureData = characteristic.decode_value(test_data)
        assert result.systolic == 120.0
        assert result.unit == "mmHg"
        assert result.timestamp is not None
        assert result.pulse_rate == 72.0
        assert result.user_id == 1
        assert result.measurement_status == 1

    def test_blood_pressure_kpa_units(self, characteristic: BloodPressureMeasurementCharacteristic) -> None:
        """Test blood pressure measurement with kPa units."""
        test_data = bytearray(
            [
                0x01,  # flags: kPa units
                0x10,
                0x00,  # systolic 16.0 kPa
                0x0B,
                0x00,  # diastolic 11.0 kPa
                0x0C,
                0x00,  # MAP 12.0 kPa
            ]
        )

        result: BloodPressureData = characteristic.decode_value(test_data)
        assert result.systolic == 16.0
        assert result.diastolic == 11.0
        assert result.mean_arterial_pressure == 12.0
        assert result.unit == "kPa"

    def test_blood_pressure_invalid_data(self, characteristic: BloodPressureMeasurementCharacteristic) -> None:
        """Test blood pressure measurement with invalid data."""
        # Test data too short
        with pytest.raises(ValueError, match="must be at least 7 bytes"):
            characteristic.decode_value(bytearray([0x00, 0x78]))
