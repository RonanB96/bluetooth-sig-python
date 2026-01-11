"""Test glucose measurement characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics.glucose_measurement import (
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementData,
    GlucoseMeasurementFlags,
    GlucoseType,
    SampleLocation,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGlucoseMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Glucose Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> GlucoseMeasurementCharacteristic:
        """Fixture providing a glucose measurement characteristic."""
        return GlucoseMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for glucose measurement characteristic."""
        return "2A18"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for glucose measurement characteristic covering various flag combinations."""
        return [
            # Test 1: Basic measurement (mg/dL, no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields, mg/dL unit
                        0x2A,
                        0x00,  # sequence number = 42
                        0xE8,
                        0x07,
                        0x03,
                        0x0F,
                        0x0E,
                        0x1E,
                        0x2D,  # timestamp: 2024-03-15 14:30:45
                        0x78,
                        0x80,  # glucose concentration 120.0 mg/dL as SFLOAT
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=42,
                    base_time=datetime.datetime(2024, 3, 15, 14, 30, 45),
                    glucose_concentration=120.0,
                    unit="mg/dL",
                    flags=GlucoseMeasurementFlags(0),
                    time_offset_minutes=None,
                    glucose_type=None,
                    sample_location=None,
                    sensor_status=None,
                    min_length=12,
                    max_length=17,
                ),
                description="Basic 120.0 mg/dL glucose measurement",
            ),
            # Test 2: mmol/L unit with time offset
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,  # flags: time offset present + mmol/L unit
                        0x15,
                        0x00,  # sequence number = 21
                        0xE8,
                        0x07,
                        0x06,
                        0x14,
                        0x08,
                        0x00,
                        0x00,  # timestamp: 2024-06-20 08:00:00
                        0x5A,
                        0x00,  # time offset +90 minutes
                        0x1E,
                        0x80,  # glucose concentration 30.0 mmol/L as SFLOAT
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=21,
                    base_time=datetime.datetime(2024, 6, 20, 8, 0, 0),
                    glucose_concentration=30.0,
                    unit="mmol/L",
                    flags=GlucoseMeasurementFlags.TIME_OFFSET_PRESENT
                    | GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L,
                    time_offset_minutes=90,
                    glucose_type=None,
                    sample_location=None,
                    sensor_status=None,
                    min_length=12,
                    max_length=17,
                ),
                description="30.0 mmol/L glucose with +90min offset",
            ),
            # Test 3: With type and sample location
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: type/sample location present, mg/dL unit
                        0x07,
                        0x00,  # sequence number = 7
                        0xE8,
                        0x07,
                        0x04,
                        0x0A,
                        0x0F,
                        0x14,
                        0x28,  # timestamp: 2024-04-10 15:20:40
                        0xAA,
                        0x80,  # glucose concentration 170.0 mg/dL as SFLOAT
                        0x21,  # type=capillary plasma (2), location=finger (1)
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=7,
                    base_time=datetime.datetime(2024, 4, 10, 15, 20, 40),
                    glucose_concentration=170.0,
                    unit="mg/dL",
                    flags=GlucoseMeasurementFlags.TYPE_SAMPLE_LOCATION_PRESENT,
                    time_offset_minutes=None,
                    glucose_type=GlucoseType.CAPILLARY_PLASMA,
                    sample_location=SampleLocation.FINGER,
                    sensor_status=None,
                    min_length=12,
                    max_length=17,
                ),
                description="170.0 mg/dL capillary plasma from finger",
            ),
            # Test 4: With sensor status annunciation
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x08,  # flags: sensor status present, mg/dL unit
                        0x64,
                        0x00,  # sequence number = 100
                        0xE8,
                        0x07,
                        0x05,
                        0x1F,
                        0x0C,
                        0x1E,
                        0x00,  # timestamp: 2024-05-31 12:30:00
                        0x64,
                        0x80,  # glucose concentration 100.0 mg/dL as SFLOAT
                        0x01,
                        0x00,  # sensor status = device battery low
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=100,
                    base_time=datetime.datetime(2024, 5, 31, 12, 30, 0),
                    glucose_concentration=100.0,
                    unit="mg/dL",
                    flags=GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT,
                    time_offset_minutes=None,
                    glucose_type=None,
                    sample_location=None,
                    sensor_status=1,  # Device battery low
                    min_length=12,
                    max_length=17,
                ),
                description="100.0 mg/dL with battery low status",
            ),
            # Test 5: Complex measurement with all optional fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0F,  # flags: all fields present + mmol/L
                        0xFF,
                        0x00,  # sequence number = 255
                        0xE8,
                        0x07,
                        0x07,
                        0x04,
                        0x10,
                        0x2D,
                        0x14,  # timestamp: 2024-07-04 16:45:20
                        0xEC,
                        0xFF,  # time offset -20 minutes (signed)
                        0x73,
                        0x80,  # glucose concentration 115 as SFLOAT
                        0x33,  # type=venous whole blood (3), location=earlobe (3)
                        0x20,
                        0x00,  # sensor status = strip insertion error
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=255,
                    base_time=datetime.datetime(2024, 7, 4, 16, 45, 20),
                    glucose_concentration=115,
                    unit="mmol/L",
                    flags=(
                        GlucoseMeasurementFlags.TIME_OFFSET_PRESENT
                        | GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L
                        | GlucoseMeasurementFlags.TYPE_SAMPLE_LOCATION_PRESENT
                        | GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT
                    ),
                    time_offset_minutes=-20,
                    glucose_type=GlucoseType.VENOUS_WHOLE_BLOOD,
                    sample_location=SampleLocation.EARLOBE,
                    sensor_status=32,  # Strip insertion error
                    min_length=12,
                    max_length=17,
                ),
                description="Complex glucose measurement with all fields",
            ),
        ]

    def test_glucose_measurement_basic_parsing(
        self, characteristic: GlucoseMeasurementCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test basic glucose measurement data parsing."""
        # Use the first test case (basic measurement)
        test_data = valid_test_data[0].input_data

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.sequence_number == 42
        assert result.glucose_concentration == 120.0
        assert result.glucose_type is None
        assert result.sample_location is None

    def test_glucose_measurement_with_type_location(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with type and location."""
        # Flags: 0x06 (Type and Sample Location Present)
        test_data = bytearray(
            [
                0x06,  # flags: type/location present
                0x01,
                0x00,  # sequence number = 1
                0xE8,
                0x07,
                0x01,
                0x0F,
                0x0A,
                0x1E,
                0x00,  # timestamp
                0x40,
                0x16,  # glucose: 100.0 mg/dL as SFLOAT
                0x11,  # type/location: 0x11 = capillary whole blood (1), finger (1)
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.glucose_type == GlucoseType.CAPILLARY_WHOLE_BLOOD
        assert result.sample_location == SampleLocation.FINGER

    def test_glucose_measurement_with_sensor_status(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with sensor status."""
        # Flags: 0x08 (Sensor Status Annunciation Present)
        test_data = bytearray(
            [
                0x08,  # flags: sensor status present
                0x01,
                0x00,  # sequence number = 1
                0xE8,
                0x07,
                0x01,
                0x0F,
                0x0A,
                0x1E,
                0x00,  # timestamp
                0x40,
                0x16,  # glucose: 100.0 mg/dL as SFLOAT
                0x01,
                0x00,  # sensor status: device battery low
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.sensor_status == 1

    def test_glucose_measurement_invalid_data(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with invalid data."""
        # Too short data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x01]))
        assert "at least 12 bytes" in str(exc_info.value)

    def test_glucose_type_names(self) -> None:
        """Test glucose type name mapping."""
        assert str(GlucoseType.CAPILLARY_WHOLE_BLOOD) == "Capillary Whole blood"
        assert str(GlucoseType.INTERSTITIAL_FLUID) == "Interstitial Fluid (ISF)"

    def test_sample_location_names(self) -> None:
        """Test sample location name mapping."""
        assert str(SampleLocation.FINGER) == "Finger"
        assert str(SampleLocation.ALTERNATE_SITE_TEST) == "Alternate Site Test (AST)"
