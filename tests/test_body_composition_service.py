"""Tests for Body Composition Service and related characteristics."""

import pytest

from bluetooth_sig.gatt.characteristics.body_composition_feature import (
    BodyCompositionFeatureCharacteristic,
)
from bluetooth_sig.gatt.characteristics.body_composition_measurement import (
    BodyCompositionMeasurementCharacteristic,
)
from bluetooth_sig.gatt.services.body_composition import BodyCompositionService


class TestBodyCompositionMeasurementCharacteristic:
    """Test Body Composition Measurement characteristic implementation."""

    def test_characteristic_name(self):
        """Test characteristic name resolution."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())
        assert char._characteristic_name == "Body Composition Measurement"
        assert char.value_type == "string"

    def test_parse_basic_body_fat_metric(self):
        """Test parsing basic body fat percentage in metric units."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x0000 (metric units), Body Fat: 250 (25.0% with 0.1% resolution)
        data = bytearray([0x00, 0x00, 0xFA, 0x00])  # 0x00FA = 250
        result = char.parse_value(data)

        assert "body_fat_percentage" in result
        assert result["body_fat_percentage"] == pytest.approx(25.0, abs=0.1)
        assert result["measurement_units"] == "metric"

    def test_parse_body_fat_imperial(self):
        """Test parsing body fat percentage in imperial units."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x0001 (imperial units), Body Fat: 180 (18.0%)
        data = bytearray([0x01, 0x00, 0xB4, 0x00])  # 0x00B4 = 180
        result = char.parse_value(data)

        assert "body_fat_percentage" in result
        assert result["body_fat_percentage"] == pytest.approx(18.0, abs=0.1)
        assert result["measurement_units"] == "imperial"

    def test_parse_with_user_id(self):
        """Test parsing with user ID."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x0004 (user ID present), Body Fat: 250, User ID: 3
        data = bytearray([0x04, 0x00, 0xFA, 0x00, 0x03])
        result = char.parse_value(data)

        assert "body_fat_percentage" in result
        assert "user_id" in result
        assert result["user_id"] == 3

    def test_parse_with_muscle_mass_metric(self):
        """Test parsing with muscle mass in metric units."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x0010 (muscle mass present), Body Fat: 250,
        # Muscle Mass: 10000 (50.0 kg)
        data = bytearray([0x10, 0x00, 0xFA, 0x00, 0x10, 0x27])  # 0x2710 = 10000
        result = char.parse_value(data)

        assert "body_fat_percentage" in result
        assert "muscle_mass" in result
        assert result["muscle_mass"] == pytest.approx(50.0, abs=0.01)  # 10000 * 0.005
        assert result["muscle_mass_unit"] == "kg"

    def test_parse_with_muscle_mass_imperial(self):
        """Test parsing with muscle mass in imperial units."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x0011 (imperial + muscle mass), Body Fat: 250,
        # Muscle Mass: 11000 (110.0 lb)
        data = bytearray([0x11, 0x00, 0xFA, 0x00, 0xF8, 0x2A])  # 0x2AF8 = 11000
        result = char.parse_value(data)

        assert "body_fat_percentage" in result
        assert "muscle_mass" in result
        assert result["muscle_mass"] == pytest.approx(110.0, abs=0.01)  # 11000 * 0.01
        assert result["muscle_mass_unit"] == "lb"

    def test_parse_invalid_data(self):
        """Test parsing with invalid data."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())

        # Too short data
        with pytest.raises(ValueError, match="at least 4 bytes"):
            char.parse_value(bytearray([0x00, 0x00, 0xFA]))

    def test_unit_property(self):
        """Test unit property."""
        char = BodyCompositionMeasurementCharacteristic(uuid="", properties=set())
        assert char.unit == "%"


class TestBodyCompositionFeatureCharacteristic:
    """Test Body Composition Feature characteristic implementation."""

    def test_characteristic_name(self):
        """Test characteristic name resolution."""
        char = BodyCompositionFeatureCharacteristic(uuid="", properties=set())
        assert char._characteristic_name == "Body Composition Feature"
        assert char.value_type == "string"

    def test_parse_basic_features(self):
        """Test parsing basic feature flags."""
        char = BodyCompositionFeatureCharacteristic(uuid="", properties=set())

        # Features: 0x0000001F (timestamp, multiple users, basal metabolism,
        # muscle mass, muscle %)
        data = bytearray([0x1F, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result["timestamp_supported"] is True
        assert result["multiple_users_supported"] is True
        assert result["basal_metabolism_supported"] is True
        assert result["muscle_mass_supported"] is True
        assert result["muscle_percentage_supported"] is True

    def test_parse_no_features(self):
        """Test parsing with no features enabled."""
        char = BodyCompositionFeatureCharacteristic(uuid="", properties=set())

        # Features: 0x00000000 (no features)
        data = bytearray([0x00, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result["timestamp_supported"] is False
        assert result["multiple_users_supported"] is False
        assert result["basal_metabolism_supported"] is False
        assert result["muscle_mass_supported"] is False
        assert result["muscle_percentage_supported"] is False

    def test_parse_invalid_data(self):
        """Test parsing with invalid data."""
        char = BodyCompositionFeatureCharacteristic(uuid="", properties=set())

        # Too short data
        with pytest.raises(ValueError, match="at least 4 bytes"):
            char.parse_value(bytearray([0x00, 0x00, 0x00]))

    def test_unit_property(self):
        """Test unit property (should be empty for feature characteristic)."""
        char = BodyCompositionFeatureCharacteristic(uuid="", properties=set())
        assert char.unit == ""


class TestBodyCompositionService:
    """Test Body Composition Service implementation."""

    def test_expected_characteristics(self):
        """Test expected characteristics for the service."""
        expected = BodyCompositionService.get_expected_characteristics()

        assert "Body Composition Measurement" in expected
        assert "Body Composition Feature" in expected
        assert (
            expected["Body Composition Measurement"]
            == BodyCompositionMeasurementCharacteristic
        )
        assert (
            expected["Body Composition Feature"] == BodyCompositionFeatureCharacteristic
        )

    def test_required_characteristics(self):
        """Test required characteristics for the service."""
        required = BodyCompositionService.get_required_characteristics()

        assert "Body Composition Measurement" in required
        assert (
            required["Body Composition Measurement"]
            == BodyCompositionMeasurementCharacteristic
        )
        # Body Composition Feature is not required

    def test_service_creation(self):
        """Test service instantiation."""
        service = BodyCompositionService()
        assert service is not None
