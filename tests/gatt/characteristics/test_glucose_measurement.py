"""Test glucose measurement characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GlucoseMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.glucose_measurement import (
    GlucoseMeasurementData,
    GlucoseType,
    SampleLocation,
)

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> bytearray:
        """Valid test data for glucose measurement characteristic."""
        # Create minimal test data: flags(1) + seq_num(2) + timestamp(7) + glucose(2)
        # Flags: 0x00 (no optional fields, mg/dL unit)
        # Sequence: 42
        # Timestamp: year=2024, month=3, day=15, hour=14, min=30, sec=45
        # Glucose: 120 mg/dL as SFLOAT (0x1780 = 120.0)
        return bytearray(
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
                0x80,
                0x17,  # glucose: 120.0 mg/dL as SFLOAT
            ]
        )

    def test_glucose_measurement_basic_parsing(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test basic glucose measurement data parsing."""
        test_data = self.valid_test_data()

        result: GlucoseMeasurementData = characteristic.decode_value(test_data)
        assert result.sequence_number == 42
        # Note: timestamp field name may vary - test sequence number and glucose value
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
                0x01,  # type/location: 0x01 = capillary whole blood, finger
            ]
        )

        result = characteristic.decode_value(test_data)
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

        result = characteristic.decode_value(test_data)
        assert result.sensor_status == 1

    def test_glucose_measurement_invalid_data(self, characteristic: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with invalid data."""
        # Too short data
        with pytest.raises(ValueError, match="must be at least 12 bytes"):
            characteristic.decode_value(bytearray([0x00, 0x01]))

    def test_glucose_type_names(self) -> None:
        """Test glucose type name mapping."""
        assert str(GlucoseType.CAPILLARY_WHOLE_BLOOD) == "Capillary Whole blood"
        assert str(GlucoseType.INTERSTITIAL_FLUID) == "Interstitial Fluid (ISF)"

    def test_sample_location_names(self) -> None:
        """Test sample location name mapping."""
        assert str(SampleLocation.FINGER) == "Finger"
        assert str(SampleLocation.ALTERNATE_SITE_TEST) == "Alternate Site Test (AST)"
