"""Test glucose monitoring service and characteristics."""

import pytest

from bluetooth_sig.gatt.characteristics import (
    GlucoseFeatureCharacteristic,
    GlucoseMeasurementCharacteristic,
    GlucoseMeasurementContextCharacteristic,
)
from bluetooth_sig.gatt.services import GlucoseService


class TestGlucoseService:
    """Test Glucose Service functionality."""

    def test_glucose_service_instantiation(self):
        """Test that glucose service can be instantiated properly."""
        service = GlucoseService()
        assert service.SERVICE_UUID == "1808"
        assert service.name == "Glucose"

    def test_glucose_service_characteristics(self):
        """Test that glucose service has correct characteristics."""
        service = GlucoseService()
        expected_chars = service.get_expected_characteristics()
        required_chars = service.get_required_characteristics()

        # Check expected characteristics
        assert "Glucose Measurement" in expected_chars
        assert "Glucose Measurement Context" in expected_chars
        assert "Glucose Feature" in expected_chars
        assert len(expected_chars) == 3

        # Check required characteristics
        assert "Glucose Measurement" in required_chars
        assert "Glucose Feature" in required_chars
        assert len(required_chars) == 2


class TestGlucoseMeasurementCharacteristic:
    """Test Glucose Measurement characteristic functionality."""

    @pytest.fixture
    def glucose_measurement_char(self):
        """Fixture providing a glucose measurement characteristic."""
        return GlucoseMeasurementCharacteristic(uuid="2A18", properties=set())

    def test_glucose_measurement_instantiation(self, glucose_measurement_char):
        """Test that glucose measurement characteristic can be instantiated."""
        assert glucose_measurement_char.CHAR_UUID == "2A18"
        assert glucose_measurement_char.value_type == "float"
        assert glucose_measurement_char.unit == "mg/dL or mmol/L"
        assert glucose_measurement_char.state_class == "measurement"

    def test_glucose_measurement_basic_parsing(self, glucose_measurement_char):
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

        result = glucose_measurement_char.parse_value(test_data)

        assert result["sequence_number"] == 42
        assert result["unit"] == "mg/dL"
        assert result["flags"] == 0
        assert "base_time" in result
        assert result["base_time"]["year"] == 2024
        assert result["base_time"]["month"] == 3
        assert result["base_time"]["day"] == 15
        assert result["base_time"]["hours"] == 14
        assert result["base_time"]["minutes"] == 30
        assert result["base_time"]["seconds"] == 45

    def test_glucose_measurement_with_mmol_unit(self, glucose_measurement_char):
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

        result = glucose_measurement_char.parse_value(test_data)
        assert result["unit"] == "mmol/L"

    def test_glucose_measurement_with_time_offset(self, glucose_measurement_char):
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

        result = glucose_measurement_char.parse_value(test_data)
        assert result["time_offset_minutes"] == 15

    def test_glucose_measurement_with_type_location(self, glucose_measurement_char):
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

        result = glucose_measurement_char.parse_value(test_data)
        assert result["glucose_type"] == 2
        assert result["sample_location"] == 1

    def test_glucose_measurement_with_sensor_status(self, glucose_measurement_char):
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

        result = glucose_measurement_char.parse_value(test_data)
        assert result["sensor_status"] == 1

    def test_glucose_measurement_invalid_data(self, glucose_measurement_char):
        """Test glucose measurement with invalid data."""
        # Too short data
        with pytest.raises(ValueError, match="must be at least 12 bytes"):
            glucose_measurement_char.parse_value(bytearray([0x00, 0x01]))

    def test_glucose_type_names(self, glucose_measurement_char):
        """Test glucose type name mapping."""
        assert (
            glucose_measurement_char._get_glucose_type_name(1)
            == "Capillary Whole blood"
        )
        assert (
            glucose_measurement_char._get_glucose_type_name(9)
            == "Interstitial Fluid (ISF)"
        )
        assert glucose_measurement_char._get_glucose_type_name(99) == "Reserved"

    def test_sample_location_names(self, glucose_measurement_char):
        """Test sample location name mapping."""
        assert glucose_measurement_char._get_sample_location_name(1) == "Finger"
        assert (
            glucose_measurement_char._get_sample_location_name(2)
            == "Alternate Site Test (AST)"
        )
        assert glucose_measurement_char._get_sample_location_name(99) == "Reserved"


class TestGlucoseMeasurementContextCharacteristic:
    """Test Glucose Measurement Context characteristic functionality."""

    @pytest.fixture
    def glucose_context_char(self):
        """Fixture providing a glucose measurement context characteristic."""
        return GlucoseMeasurementContextCharacteristic(uuid="2A34", properties=set())

    def test_glucose_context_instantiation(self, glucose_context_char):
        """Test that glucose context characteristic can be instantiated."""
        assert glucose_context_char.CHAR_UUID == "2A34"
        assert glucose_context_char.value_type == "string"
        assert glucose_context_char.unit == "various"

    def test_glucose_context_basic_parsing(self, glucose_context_char):
        """Test basic glucose context data parsing."""
        # Create minimal test data: flags(1) + seq_num(2)
        test_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence number = 42
            ]
        )

        result = glucose_context_char.parse_value(test_data)
        assert result["sequence_number"] == 42
        assert result["flags"] == 0

    def test_glucose_context_with_carbohydrate(self, glucose_context_char):
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

        result = glucose_context_char.parse_value(test_data)
        assert result["carbohydrate_id"] == 1
        assert result["carbohydrate_type"] == "Breakfast"

    def test_glucose_context_with_meal(self, glucose_context_char):
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

        result = glucose_context_char.parse_value(test_data)
        assert result["meal"] == 2
        assert result["meal_type"] == "Postprandial (after meal)"

    def test_glucose_context_with_exercise(self, glucose_context_char):
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

        result = glucose_context_char.parse_value(test_data)
        assert result["exercise_duration_seconds"] == 600
        assert result["exercise_intensity_percent"] == 75

    def test_glucose_context_with_hba1c(self, glucose_context_char):
        """Test glucose context with HbA1c data."""
        # Flags: 0x40 (HbA1c present)
        test_data = bytearray(
            [
                0x40,  # flags: HbA1c present
                0x01,
                0x00,  # sequence number = 1
                0x80,
                0x18,  # HbA1c: 7.2% as SFLOAT
            ]
        )

        result = glucose_context_char.parse_value(test_data)
        assert "hba1c_percent" in result

    def test_glucose_context_type_names(self, glucose_context_char):
        """Test context type name mappings."""
        assert glucose_context_char._get_carbohydrate_type_name(1) == "Breakfast"
        assert glucose_context_char._get_meal_type_name(3) == "Fasting"
        assert (
            glucose_context_char._get_tester_type_name(2) == "Health Care Professional"
        )
        assert glucose_context_char._get_health_type_name(5) == "No health issues"
        assert (
            glucose_context_char._get_medication_type_name(1) == "Rapid acting insulin"
        )

    def test_glucose_context_invalid_data(self, glucose_context_char):
        """Test glucose context with invalid data."""
        with pytest.raises(ValueError, match="must be at least 3 bytes"):
            glucose_context_char.parse_value(bytearray([0x00]))


class TestGlucoseFeatureCharacteristic:
    """Test Glucose Feature characteristic functionality."""

    @pytest.fixture
    def glucose_feature_char(self):
        """Fixture providing a glucose feature characteristic."""
        return GlucoseFeatureCharacteristic(uuid="2A51", properties=set())

    def test_glucose_feature_instantiation(self, glucose_feature_char):
        """Test that glucose feature characteristic can be instantiated."""
        assert glucose_feature_char.CHAR_UUID == "2A51"
        assert glucose_feature_char.value_type == "int"
        assert glucose_feature_char.unit == "bitmap"

    def test_glucose_feature_basic_parsing(self, glucose_feature_char):
        """Test basic glucose feature parsing."""
        # Features: 0x0403 = Low Battery + Sensor Malfunction + Multiple Bond
        test_data = bytearray([0x03, 0x04])

        result = glucose_feature_char.parse_value(test_data)
        assert result["features_bitmap"] == 0x0403
        assert result["low_battery_detection"] is True
        assert result["sensor_malfunction_detection"] is True
        assert result["multiple_bond_support"] is True
        assert result["sensor_sample_size"] is False
        assert len(result["enabled_features"]) == 3

    def test_glucose_feature_all_features(self, glucose_feature_char):
        """Test glucose feature with all features enabled."""
        # All feature bits set
        test_data = bytearray([0xFF, 0x07])  # All 11 defined feature bits

        result = glucose_feature_char.parse_value(test_data)
        assert result["feature_count"] == 11
        assert "Low Battery Detection" in result["enabled_features"]
        assert "Multiple Bond Support" in result["enabled_features"]

    def test_glucose_feature_no_features(self, glucose_feature_char):
        """Test glucose feature with no features enabled."""
        test_data = bytearray([0x00, 0x00])

        result = glucose_feature_char.parse_value(test_data)
        assert result["features_bitmap"] == 0
        assert result["feature_count"] == 0
        assert len(result["enabled_features"]) == 0

    def test_glucose_feature_descriptions(self, glucose_feature_char):
        """Test feature bit descriptions."""
        assert "Low Battery Detection" in glucose_feature_char.get_feature_description(
            0
        )
        assert "Multiple Bond" in glucose_feature_char.get_feature_description(10)
        assert "Reserved" in glucose_feature_char.get_feature_description(15)

    def test_glucose_feature_invalid_data(self, glucose_feature_char):
        """Test glucose feature with invalid data."""
        with pytest.raises(ValueError, match="must be at least 2 bytes"):
            glucose_feature_char.parse_value(bytearray([0x00]))


class TestGlucoseIntegration:
    """Test glucose service integration with the framework."""

    def test_glucose_service_registration(self):
        """Test that glucose service is properly registered."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Check that glucose service is in the registry
        service_class = GattServiceRegistry.get_service_class("1808")
        assert service_class == GlucoseService

        # Check that glucose service can be instantiated correctly
        glucose_service = service_class()
        assert glucose_service.SERVICE_UUID == "1808"

    def test_glucose_characteristics_registration(self):
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

    def test_glucose_service_creation(self):
        """Test glucose service creation with characteristics."""
        from bluetooth_sig.gatt.services import GattServiceRegistry

        # Simulate characteristics data
        characteristics = {
            "00002a18-0000-1000-8000-00805f9b34fb": {"properties": ["read", "notify"]},
            "00002a34-0000-1000-8000-00805f9b34fb": {"properties": ["read", "notify"]},
            "00002a51-0000-1000-8000-00805f9b34fb": {"properties": ["read"]},
        }

        service = GattServiceRegistry.create_service("1808", characteristics)
        assert service is not None
        assert isinstance(service, GlucoseService)
        assert len(service.characteristics) == 3
