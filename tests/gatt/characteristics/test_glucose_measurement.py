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
        """Valid test data for glucose measurement characteristic covering various flag combinations.

        Per GSS YAML:
          bit 0: Time Offset present
          bit 1: Glucose Concentration + Type-Sample Location present
          bit 2: Glucose Units (0=mg/dL, 1=mmol/L)
          bit 3: Sensor Status Annunciation present
        Type-Sample Location byte: low nibble = Type, high nibble = Sample Location.
        """
        return [
            # Test 1: Mandatory fields only (no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0x2A,
                        0x00,  # sequence number = 42
                        0xE8,
                        0x07,
                        0x03,
                        0x0F,
                        0x0E,
                        0x1E,
                        0x2D,  # timestamp: 2024-03-15 14:30:45
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=42,
                    base_time=datetime.datetime(2024, 3, 15, 14, 30, 45),
                    flags=GlucoseMeasurementFlags(0),
                    min_length=10,
                    max_length=17,
                ),
                description="Mandatory fields only (no concentration)",
            ),
            # Test 2: With concentration (mg/dL) + type-sample location
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: bit1 = concentration+type-sample present, mg/dL (bit2=0)
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
                        0x12,  # type=capillary plasma (2) in HIGH nibble=1... wait
                        # type in LOW nibble: 2=capillary plasma; location in HIGH nibble: 1=finger
                        # byte = (1 << 4) | 2 = 0x12
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=42,
                    base_time=datetime.datetime(2024, 3, 15, 14, 30, 45),
                    flags=GlucoseMeasurementFlags.CONCENTRATION_TYPE_SAMPLE_PRESENT,
                    glucose_concentration=120.0,
                    unit="mg/dL",
                    glucose_type=GlucoseType.CAPILLARY_PLASMA,
                    sample_location=SampleLocation.FINGER,
                    min_length=10,
                    max_length=17,
                ),
                description="120.0 mg/dL capillary plasma from finger",
            ),
            # Test 3: mmol/L unit with time offset
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x07,  # flags: bit0=time offset, bit1=conc+type, bit2=mmol/L
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
                        0x11,  # type=capillary whole blood (1), location=finger (1)
                        # byte = (1 << 4) | 1 = 0x11
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=21,
                    base_time=datetime.datetime(2024, 6, 20, 8, 0, 0),
                    flags=GlucoseMeasurementFlags.TIME_OFFSET_PRESENT
                    | GlucoseMeasurementFlags.CONCENTRATION_TYPE_SAMPLE_PRESENT
                    | GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L,
                    glucose_concentration=30.0,
                    unit="mmol/L",
                    time_offset_minutes=90,
                    glucose_type=GlucoseType.CAPILLARY_WHOLE_BLOOD,
                    sample_location=SampleLocation.FINGER,
                    min_length=10,
                    max_length=17,
                ),
                description="30.0 mmol/L glucose with +90min offset",
            ),
            # Test 4: With sensor status annunciation
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0A,  # flags: bit1=conc+type present, bit3=sensor status
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
                        0xF1,  # type=capillary whole blood (1), location=not available (0xF)
                        # byte = (0xF << 4) | 1 = 0xF1
                        0x01,
                        0x00,  # sensor status = device battery low
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=100,
                    base_time=datetime.datetime(2024, 5, 31, 12, 30, 0),
                    flags=GlucoseMeasurementFlags.CONCENTRATION_TYPE_SAMPLE_PRESENT
                    | GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT,
                    glucose_concentration=100.0,
                    unit="mg/dL",
                    glucose_type=GlucoseType.CAPILLARY_WHOLE_BLOOD,
                    sample_location=SampleLocation.NOT_AVAILABLE,
                    sensor_status=1,
                    min_length=10,
                    max_length=17,
                ),
                description="100.0 mg/dL with battery low status",
            ),
            # Test 5: All optional fields present
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0F,  # flags: bits 0-3 all set (time+conc+mmol/L+sensor)
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
                        # byte = (3 << 4) | 3 = 0x33
                        0x20,
                        0x00,  # sensor status = strip insertion error
                    ]
                ),
                expected_value=GlucoseMeasurementData(
                    sequence_number=255,
                    base_time=datetime.datetime(2024, 7, 4, 16, 45, 20),
                    flags=(
                        GlucoseMeasurementFlags.TIME_OFFSET_PRESENT
                        | GlucoseMeasurementFlags.CONCENTRATION_TYPE_SAMPLE_PRESENT
                        | GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L
                        | GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT
                    ),
                    glucose_concentration=115,
                    unit="mmol/L",
                    time_offset_minutes=-20,
                    glucose_type=GlucoseType.VENOUS_WHOLE_BLOOD,
                    sample_location=SampleLocation.EARLOBE,
                    sensor_status=32,
                    min_length=10,
                    max_length=17,
                ),
                description="Complex glucose measurement with all fields",
            ),
        ]

    def test_glucose_measurement_basic_parsing(
        self, characteristic: GlucoseMeasurementCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test basic glucose measurement data parsing (mandatory fields only)."""
        test_data = valid_test_data[0].input_data

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.sequence_number == 42
        assert result.glucose_concentration is None
        assert result.glucose_type is None
        assert result.sample_location is None

    def test_glucose_measurement_with_type_location(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with type and location.

        Per GSS YAML bit 1 = concentration+type-sample present.
        Type-Sample byte: low nibble = type, high nibble = sample location.
        0x11: type=1 (capillary whole blood), location=1 (finger).
        """
        test_data = bytearray(
            [
                0x02,  # flags: bit1 = conc+type-sample present, mg/dL
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
                0x16,  # glucose: SFLOAT
                0x11,  # type/location: low=1 (capillary whole blood), high=1 (finger)
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.glucose_type == GlucoseType.CAPILLARY_WHOLE_BLOOD
        assert result.sample_location == SampleLocation.FINGER

    def test_glucose_measurement_with_sensor_status(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with sensor status (no concentration)."""
        test_data = bytearray(
            [
                0x08,  # flags: bit3 = sensor status present (no concentration)
                0x01,
                0x00,  # sequence number = 1
                0xE8,
                0x07,
                0x01,
                0x0F,
                0x0A,
                0x1E,
                0x00,  # timestamp
                0x01,
                0x00,  # sensor status: device battery low
            ]
        )

        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.sensor_status == 1
        assert result.glucose_concentration is None

    def test_glucose_measurement_invalid_data(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with invalid data."""
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x01]))
        assert "at least 10 bytes" in str(exc_info.value)

    def test_glucose_type_names(self) -> None:
        """Test glucose type name mapping."""
        assert str(GlucoseType.CAPILLARY_WHOLE_BLOOD) == "Capillary Whole blood"
        assert str(GlucoseType.INTERSTITIAL_FLUID) == "Interstitial Fluid (ISF)"

    def test_sample_location_names(self) -> None:
        """Test sample location name mapping."""
        assert str(SampleLocation.FINGER) == "Finger"
        assert str(SampleLocation.ALTERNATE_SITE_TEST) == "Alternate Site Test (AST)"
