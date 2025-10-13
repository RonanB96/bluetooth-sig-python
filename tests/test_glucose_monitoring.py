"""Test glucose monitoring service and characteristics."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    GlucoseFeatureCharacteristic,
    GlucoseFeatures,
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementContextCharacteristic,
    GlucoseMeasurementContextFlags,
)
from bluetooth_sig.gatt.characteristics.glucose_measurement import (
    GlucoseMeasurementData,
    GlucoseType,
    SampleLocation,
)
from bluetooth_sig.gatt.characteristics.glucose_measurement_context import (
    CarbohydrateType,
    GlucoseTester,
    HealthType,
    MealType,
    MedicationType,
)
from bluetooth_sig.gatt.services.glucose import GlucoseService
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.types.gatt_services import ServiceDiscoveryData
from bluetooth_sig.types.uuid import BluetoothUUID


class TestGlucoseService:
    """Test Glucose Service functionality."""

    def test_glucose_service_instantiation(self) -> None:
        """Test that glucose service can be instantiated properly."""
        service = GlucoseService()
        assert service.uuid == "1808"
        assert service.name == "Glucose"

    def test_glucose_service_characteristics(self) -> None:
        """Test that glucose service has correct characteristics."""
        service = GlucoseService()
        expected_chars = service.get_expected_characteristics()
        required_chars = service.get_required_characteristics()
        # Check expected characteristics
        assert CharacteristicName.GLUCOSE_MEASUREMENT in expected_chars
        assert CharacteristicName.GLUCOSE_MEASUREMENT_CONTEXT in expected_chars
        assert CharacteristicName.GLUCOSE_FEATURE in expected_chars
        assert len(expected_chars) == 3

        # Check required characteristics
        assert CharacteristicName.GLUCOSE_MEASUREMENT in required_chars
        assert CharacteristicName.GLUCOSE_FEATURE in required_chars
        assert len(required_chars) == 2


class TestGlucoseMeasurementCharacteristic:
    """Test Glucose Measurement characteristic functionality."""

    @pytest.fixture
    def glucose_measurement_char(self) -> GlucoseMeasurementCharacteristic:
        """Fixture providing a glucose measurement characteristic."""
        return GlucoseMeasurementCharacteristic()

    def test_glucose_measurement_instantiation(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test that glucose measurement characteristic can be instantiated."""
        assert glucose_measurement_char.uuid == "2A18"
        assert glucose_measurement_char.value_type.value == "bytes"  # YAML struct type
        assert glucose_measurement_char.unit == "mg/dL or mmol/L"

    def test_glucose_measurement_basic_parsing(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test basic glucose measurement data parsing."""
        # Create minimal test data: flags(1) + seq_num(2) + timestamp(7) + glucose(2)
        # Flags: 0x00 (no optional fields, mg/dL unit)
        # Sequence: 42
        # Timestamp: year=2024, month=3, day=15, hour=14, min=30, sec=45
        # Glucose: 120 mg/dL as SFLOAT (0x1780 = 120.0)
        test_data = bytearray(
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

        result: GlucoseMeasurementData = glucose_measurement_char.decode_value(test_data)

        assert result.sequence_number == 42
        assert result.unit == "mg/dL"
        assert result.flags == 0
        # Test timestamp parsing
        assert result.base_time.year == 2024
        assert result.base_time.month == 3
        assert result.base_time.day == 15
        assert result.base_time.hour == 14
        assert result.base_time.minute == 30
        assert result.base_time.second == 45

    def test_glucose_measurement_with_mmol_unit(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test glucose measurement with mmol/L unit."""
        # Flags: 0x02 (mmol/L unit flag set)
        test_data = bytearray(
            [
                0x02,  # flags: mmol/L unit
                0x01,
                0x00,  # sequence number = 1
                0xE8,
                0x07,
                0x01,
                0x0F,
                0x0A,
                0x1E,
                0x00,  # timestamp
                0x5C,
                0x16,  # glucose: 6.7 mmol/L as SFLOAT
            ]
        )

        result = glucose_measurement_char.decode_value(test_data)
        assert result.unit == "mmol/L"

    def test_glucose_measurement_with_time_offset(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test glucose measurement with time offset."""
        # Flags: 0x01 (time offset present)
        test_data = bytearray(
            [
                0x01,  # flags: time offset present
                0x01,
                0x00,  # sequence number = 1
                0xE8,
                0x07,
                0x01,
                0x0F,
                0x0A,
                0x1E,
                0x00,  # timestamp
                0x0F,
                0x00,  # time offset: +15 minutes
                0x40,
                0x16,  # glucose: 100.0 mg/dL as SFLOAT
            ]
        )

        result = glucose_measurement_char.decode_value(test_data)
        assert result.time_offset_minutes == 15

    def test_glucose_measurement_with_type_location(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test glucose measurement with type and sample location."""
        # Flags: 0x04 (type and sample location present)
        test_data = bytearray(
            [
                0x04,  # flags: type and sample location present
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
                0x21,  # type=2 (Capillary Plasma), location=1 (Finger)
            ]
        )

        result = glucose_measurement_char.decode_value(test_data)
        assert result.glucose_type == 2
        assert result.sample_location == 1

    def test_glucose_measurement_with_sensor_status(
        self, glucose_measurement_char: GlucoseMeasurementCharacteristic
    ) -> None:
        """Test glucose measurement with sensor status."""
        # Flags: 0x08 (sensor status present)
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

        result = glucose_measurement_char.decode_value(test_data)
        assert result.sensor_status == 1

    def test_glucose_measurement_invalid_data(self, glucose_measurement_char: GlucoseMeasurementCharacteristic) -> None:
        """Test glucose measurement with invalid data."""
        # Too short data
        with pytest.raises(ValueError, match="must be at least 12 bytes"):
            glucose_measurement_char.decode_value(bytearray([0x00, 0x01]))

    def test_glucose_type_names(self) -> None:
        """Test glucose type name mapping."""
        assert str(GlucoseType.CAPILLARY_WHOLE_BLOOD) == "Capillary Whole blood"
        assert str(GlucoseType.INTERSTITIAL_FLUID) == "Interstitial Fluid (ISF)"

    def test_sample_location_names(self) -> None:
        """Test sample location name mapping."""
        assert str(SampleLocation.FINGER) == "Finger"
        assert str(SampleLocation.ALTERNATE_SITE_TEST) == "Alternate Site Test (AST)"


class TestGlucoseMeasurementContextCharacteristic:
    """Test Glucose Measurement Context characteristic functionality."""

    @pytest.fixture
    def glucose_context_char(self) -> GlucoseMeasurementContextCharacteristic:
        """Fixture providing a glucose measurement context characteristic."""
        return GlucoseMeasurementContextCharacteristic()

    def test_glucose_context_instantiation(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
        """Test that glucose context characteristic can be instantiated."""
        assert glucose_context_char.uuid == "2A34"
        assert glucose_context_char.value_type.value == "bytes"  # YAML struct type
        assert glucose_context_char.unit == "various"

    def test_glucose_context_basic_parsing(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
        """Test basic glucose context data parsing."""
        # Create minimal test data: flags(1) + seq_num(2)
        test_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence number = 42
            ]
        )

        result = glucose_context_char.decode_value(test_data)
        assert result.sequence_number == 42
        assert result.flags == GlucoseMeasurementContextFlags(0)

    def test_glucose_context_with_carbohydrate(
        self, glucose_context_char: GlucoseMeasurementContextCharacteristic
    ) -> None:
        """Test glucose context with carbohydrate data."""
        # Flags: 0x02 (carbohydrate present)
        test_data = bytearray(
            [
                0x02,  # flags: carbohydrate present
                0x01,
                0x00,  # sequence number = 1
                0x01,  # carbohydrate ID = 1 (Breakfast)
                0x40,
                0x1C,  # carbohydrate: 50.0g as SFLOAT
            ]
        )

        result = glucose_context_char.decode_value(test_data)
        assert result.carbohydrate_id == CarbohydrateType.BREAKFAST
        # Human-readable name should match the enum's string representation
        assert str(result.carbohydrate_id) == "Breakfast"

    def test_glucose_context_with_meal(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
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

        result = glucose_context_char.decode_value(test_data)
        assert result.meal == MealType.POSTPRANDIAL
        # Human-readable meal name should match the enum's string representation
        assert str(result.meal) == "Postprandial (after meal)"

    def test_glucose_context_with_exercise(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with exercise data."""
        # Flags: 0x10 (exercise present)
        test_data = bytearray(
            [
                0x10,  # flags: exercise present
                0x01,
                0x00,  # sequence number = 1
                0x58,
                0x02,  # exercise duration: 600 seconds (10 minutes)
                0x4B,  # exercise intensity: 75%
            ]
        )

        result = glucose_context_char.decode_value(test_data)
        assert result.exercise_duration_seconds == 600
        assert result.exercise_intensity_percent == 75

    def test_glucose_context_with_hba1c(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with HbA1c data."""
        # Flags: 0x40 (HbA1c present)
        test_data = bytearray(
            [
                0x40,  # flags: HbA1c present
                0x01,
                0x00,  # sequence number = 1
                0x48,
                0xF0,  # HbA1c: 7.2% as SFLOAT
            ]
        )

        result = glucose_context_char.decode_value(test_data)
        assert result.hba1c_percent == 7.2

    def test_glucose_context_type_names(self) -> None:
        """Test context type name mappings."""
        # Prefer passing the enum members (hard typing)
        assert str(CarbohydrateType.BREAKFAST) == "Breakfast"
        assert str(MealType.FASTING) == "Fasting"
        assert str(GlucoseTester.HEALTH_CARE_PROFESSIONAL) == "Health Care Professional"
        assert str(HealthType.NO_HEALTH_ISSUES) == "No health issues"
        assert str(MedicationType.RAPID_ACTING_INSULIN) == "Rapid acting insulin"

    def test_glucose_context_invalid_data(self, glucose_context_char: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with invalid data."""
        with pytest.raises(ValueError, match="must be at least 3 bytes"):
            glucose_context_char.decode_value(bytearray([0x00]))


class TestGlucoseFeatureCharacteristic:
    """Test Glucose Feature characteristic functionality."""

    @pytest.fixture
    def glucose_feature_char(self) -> GlucoseFeatureCharacteristic:
        """Fixture providing a glucose feature characteristic."""
        return GlucoseFeatureCharacteristic()

    def test_glucose_feature_instantiation(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test that glucose feature characteristic can be instantiated."""
        assert glucose_feature_char.uuid == "2A51"
        assert glucose_feature_char.value_type.value == "bytes"  # YAML struct type
        assert glucose_feature_char.unit == "bitmap"

    def test_glucose_feature_basic_parsing(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test basic glucose feature parsing."""
        # Features: 0x0403 = Low Battery + Sensor Malfunction + Multiple Bond
        test_data = bytearray([0x03, 0x04])

        result = glucose_feature_char.decode_value(test_data)
        assert result.features_bitmap == 0x0403
        assert result.low_battery_detection is True
        assert result.sensor_malfunction_detection is True
        assert result.multiple_bond_support is True
        assert result.sensor_sample_size is False
        assert len(result.enabled_features) == 3

    def test_glucose_feature_all_features(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test glucose feature with all features enabled."""
        # All feature bits set
        test_data = bytearray([0xFF, 0x07])  # All 11 defined feature bits

        result = glucose_feature_char.decode_value(test_data)
        assert result.feature_count == 11
        # enabled_features is a list of GlucoseFeatures (hard-typed)
        assert GlucoseFeatures.LOW_BATTERY_DETECTION in result.enabled_features
        assert GlucoseFeatures.MULTIPLE_BOND_SUPPORT in result.enabled_features

    def test_glucose_feature_no_features(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test glucose feature with no features enabled."""
        test_data = bytearray([0x00, 0x00])

        result = glucose_feature_char.decode_value(test_data)
        assert result.features_bitmap == 0
        assert result.feature_count == 0
        assert len(result.enabled_features) == 0

    def test_glucose_feature_descriptions(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test feature bit descriptions."""
        assert "Low Battery Detection During Measurement Supported" in glucose_feature_char.get_feature_description(
            GlucoseFeatures.LOW_BATTERY_DETECTION.value
        )
        assert "Multiple Bond Supported" in glucose_feature_char.get_feature_description(
            GlucoseFeatures.MULTIPLE_BOND_SUPPORT.value
        )
        assert "Reserved feature" in glucose_feature_char.get_feature_description(15)

    def test_glucose_feature_invalid_data(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test glucose feature with invalid data."""
        with pytest.raises(ValueError, match="must be at least 2 bytes"):
            glucose_feature_char.decode_value(bytearray([0x00]))

    def test_glucose_feature_encode_value(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test encoding GlucoseFeatureData back to bytes."""
        from bluetooth_sig.gatt.characteristics.glucose_feature import (
            GlucoseFeatureData,
        )

        # Create test data
        test_data = GlucoseFeatureData(
            features_bitmap=GlucoseFeatures(0x0403),
            low_battery_detection=True,
            sensor_malfunction_detection=True,
            sensor_sample_size=False,
            sensor_strip_insertion_error=False,
            sensor_strip_type_error=False,
            sensor_result_high_low=False,
            sensor_temperature_high_low=False,
            sensor_read_interrupt=False,
            general_device_fault=False,
            time_fault=False,
            multiple_bond_support=True,
            enabled_features=(
                GlucoseFeatures.LOW_BATTERY_DETECTION,
                GlucoseFeatures.SENSOR_MALFUNCTION_DETECTION,
                GlucoseFeatures.MULTIPLE_BOND_SUPPORT,
            ),
            feature_count=3,
        )

        # Encode the data
        encoded = glucose_feature_char.encode_value(test_data)

        # Should produce the correct bytes
        assert len(encoded) == 2
        assert encoded == bytearray([0x03, 0x04])  # Little endian 0x0403

    def test_glucose_feature_round_trip(self, glucose_feature_char: GlucoseFeatureCharacteristic) -> None:
        """Test that parsing and encoding preserve data."""
        # Test with basic features
        original_data = bytearray([0x03, 0x04])  # Low Battery + Sensor Malfunction + Multiple Bond

        # Parse the data
        parsed = glucose_feature_char.decode_value(original_data)

        # Encode it back
        encoded = glucose_feature_char.encode_value(parsed)

        # Should match the original
        assert encoded == original_data


class TestGlucoseIntegration:
    """Test glucose service integration with the framework."""

    def test_glucose_service_registration(self) -> None:
        """Test that glucose service is properly registered."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Check that glucose service is in the registry
        service_class = GattServiceRegistry.get_service_class("1808")
        assert service_class == GlucoseService

        # Check that glucose service can be instantiated correctly
        glucose_service = service_class()
        assert glucose_service.uuid == "1808"

    def test_glucose_characteristics_registration(self) -> None:
        """Test that glucose characteristics are properly registered."""
        from bluetooth_sig.gatt.characteristics import CharacteristicRegistry

        # Test Glucose Measurement
        gm_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A18")
        assert gm_class == GlucoseMeasurementCharacteristic

        # Test Glucose Measurement Context
        gmc_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A34")
        assert gmc_class == GlucoseMeasurementContextCharacteristic

        # Test Glucose Feature
        gf_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A51")
        assert gf_class == GlucoseFeatureCharacteristic

    def test_glucose_service_creation(self) -> None:
        """Test glucose service creation with characteristics."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Use characteristic classes to get proper SIG UUIDs
        glucose_measurement_char = GlucoseMeasurementCharacteristic()
        glucose_context_char = GlucoseMeasurementContextCharacteristic()
        glucose_feature_char = GlucoseFeatureCharacteristic()

        characteristics: ServiceDiscoveryData = {
            glucose_measurement_char.uuid: glucose_measurement_char.info,
            glucose_context_char.uuid: glucose_context_char.info,
            glucose_feature_char.uuid: glucose_feature_char.info,
        }

        service = GattServiceRegistry.create_service(BluetoothUUID("1808"), characteristics)
        assert service is not None
        assert isinstance(service, GlucoseService)
        assert len(service.characteristics) == 3


class TestGlucoseMultiCharacteristic:
    """Test multi-characteristic parsing with glucose measurements."""

    def test_glucose_context_with_measurement_context(self) -> None:
        """Test parsing glucose measurement and context together with sequence number matching."""
        from bluetooth_sig.core import BluetoothSIGTranslator

        translator = BluetoothSIGTranslator()

        # Create matching glucose measurement and context with same sequence number (42)
        # Glucose Measurement: Flags + Seq(42) + Timestamp + Glucose
        glucose_data = bytearray(
            [
                0x00,  # flags: no optional fields, mg/dL unit
                0x2A,
                0x00,  # sequence: 42
                0xE8,
                0x07,
                0x03,
                0x0F,
                0x0E,
                0x1E,
                0x2D,  # timestamp: 2024-03-15 14:30:45
                0x80,
                0x17,  # glucose: 120.0 mg/dL (SFLOAT)
            ]
        )

        # Glucose Context: Flags + Seq(42)
        context_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence: 42 (matches measurement)
            ]
        )

        # Parse both characteristics together
        char_data: dict[str, bytes] = {
            "00002A18-0000-1000-8000-00805F9B34FB": bytes(glucose_data),  # Glucose Measurement
            "00002A34-0000-1000-8000-00805F9B34FB": bytes(context_data),  # Glucose Measurement Context
        }

        results = translator.parse_characteristics(char_data)

        # Both should parse successfully
        assert len(results) == 2
        assert all(r.parse_success for r in results.values())

        # Check sequence numbers match
        glucose_result = results["00002A18-0000-1000-8000-00805F9B34FB"]
        context_result = results["00002A34-0000-1000-8000-00805F9B34FB"]

        assert glucose_result.value is not None
        assert context_result.value is not None
        assert glucose_result.value.sequence_number == 42
        assert context_result.value.sequence_number == 42

    def test_glucose_context_sequence_mismatch_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that mismatched sequence numbers generate a warning."""
        from bluetooth_sig.core import BluetoothSIGTranslator

        translator = BluetoothSIGTranslator()

        # Create glucose measurement and context with DIFFERENT sequence numbers
        glucose_data = bytearray(
            [
                0x00,  # flags
                0x2A,
                0x00,  # sequence: 42
                0xE8,
                0x07,
                0x03,
                0x0F,
                0x0E,
                0x1E,
                0x2D,  # timestamp
                0x80,
                0x17,  # glucose: 120.0 mg/dL
            ]
        )

        context_data = bytearray(
            [
                0x00,  # flags
                0x63,
                0x00,  # sequence: 99 (MISMATCH!)
            ]
        )

        char_data: dict[str, bytes] = {
            "00002A18-0000-1000-8000-00805F9B34FB": bytes(glucose_data),
            "00002A34-0000-1000-8000-00805F9B34FB": bytes(context_data),
        }

        # Parse both - should succeed but log warning
        import logging

        with caplog.at_level(logging.WARNING):
            results = translator.parse_characteristics(char_data)

        # Both should still parse successfully
        assert len(results) == 2
        assert all(r.parse_success for r in results.values())

        # Check that warning was logged about mismatch
        assert any("does not match" in record.message for record in caplog.records)
