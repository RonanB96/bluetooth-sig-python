"""Tests for Weight Scale Service and related characteristics."""

import pytest

from bluetooth_sig.gatt.characteristics.weight_measurement import (
    WeightMeasurementCharacteristic,
)
from bluetooth_sig.gatt.characteristics.weight_scale_feature import (
    WeightMeasurementResolution,
    WeightScaleFeatureCharacteristic,
)
from bluetooth_sig.gatt.services.weight_scale import WeightScaleService


class TestWeightMeasurementCharacteristic:
    """Test Weight Measurement characteristic implementation."""

    def test_characteristic_name(self):
        """Test characteristic name resolution."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())
        assert char._characteristic_name == "Weight Measurement"
        assert char.value_type == "bytes"

    def test_parse_basic_weight_metric(self):
        """Test parsing basic weight in metric units."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x00 (metric units), Weight: 14000 (70.00 kg with 0.005 kg resolution)
        data = bytearray([0x00, 0x70, 0x36])  # 0x3670 = 13936
        result = char.parse_value(data)

        assert "weight" in result
        assert result["weight"] == pytest.approx(69.68, abs=0.01)  # 13936 * 0.005
        assert result["weight_unit"] == "kg"
        assert result["measurement_units"] == "metric"

    def test_parse_basic_weight_imperial(self):
        """Test parsing basic weight in imperial units."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x01 (imperial units), Weight: 15000
        # (150.00 lb with 0.01 lb resolution)
        data = bytearray([0x01, 0x98, 0x3A])  # 0x3A98 = 15000
        result = char.parse_value(data)

        assert "weight" in result
        assert result["weight"] == pytest.approx(150.0, abs=0.01)  # 15000 * 0.01
        assert result["weight_unit"] == "lb"
        assert result["measurement_units"] == "imperial"

    def test_parse_weight_with_user_id(self):
        """Test parsing weight with user ID."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())

        # Flags: 0x04 (user ID present), Weight: 14000, User ID: 5
        data = bytearray([0x04, 0x70, 0x36, 0x05])
        result = char.parse_value(data)

        assert "weight" in result
        assert "user_id" in result
        assert result["user_id"] == 5

    def test_parse_invalid_data(self):
        """Test parsing with invalid data."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())

        # Too short data
        with pytest.raises(ValueError, match="at least 3 bytes"):
            char.parse_value(bytearray([0x00, 0x70]))

    def test_unit_property(self):
        """Test unit property."""
        char = WeightMeasurementCharacteristic(uuid="", properties=set())
        assert char.unit == "kg"


class TestWeightScaleFeatureCharacteristic:
    """Test Weight Scale Feature characteristic implementation."""

    def test_characteristic_name(self):
        """Test characteristic name resolution."""
        char = WeightScaleFeatureCharacteristic(uuid="", properties=set())
        assert char._characteristic_name == "Weight Scale Feature"
        assert char.value_type == "bytes"

    def test_parse_basic_features(self):
        """Test parsing basic feature flags."""
        char = WeightScaleFeatureCharacteristic(uuid="", properties=set())

        # Features: 0x0000000F (timestamp, multiple users, BMI supported,
        # weight resolution 1)
        data = bytearray([0x0F, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result.timestamp_supported is True
        assert result.multiple_users_supported is True
        assert result.bmi_supported is True
        assert (
            result.weight_measurement_resolution
            == WeightMeasurementResolution.HALF_KG_OR_1_LB
        )

    def test_parse_no_features(self):
        """Test parsing with no features enabled."""
        char = WeightScaleFeatureCharacteristic(uuid="", properties=set())

        # Features: 0x00000000 (no features)
        data = bytearray([0x00, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result.timestamp_supported is False
        assert result.multiple_users_supported is False
        assert result.bmi_supported is False
        assert (
            result.weight_measurement_resolution
            == WeightMeasurementResolution.NOT_SPECIFIED
        )

    def test_parse_invalid_data(self):
        """Test parsing with invalid data."""
        char = WeightScaleFeatureCharacteristic(uuid="", properties=set())

        # Too short data
        with pytest.raises(ValueError, match="at least 4 bytes"):
            char.parse_value(bytearray([0x00, 0x00, 0x00]))

    def test_unit_property(self):
        """Test unit property (should be empty for feature characteristic)."""
        char = WeightScaleFeatureCharacteristic(uuid="", properties=set())
        assert char.unit == ""


class TestWeightScaleService:
    """Test Weight Scale Service implementation."""

    def test_expected_characteristics(self):
        """Test expected characteristics for the service."""
        expected = WeightScaleService.get_expected_characteristics()

        assert "Weight Measurement" in expected
        assert "Weight Scale Feature" in expected
        assert expected["Weight Measurement"] == WeightMeasurementCharacteristic
        assert expected["Weight Scale Feature"] == WeightScaleFeatureCharacteristic

    def test_required_characteristics(self):
        """Test required characteristics for the service."""
        required = WeightScaleService.get_required_characteristics()

        assert "Weight Measurement" in required
        assert required["Weight Measurement"] == WeightMeasurementCharacteristic
        # Weight Scale Feature is not required

    def test_service_creation(self):
        """Test service instantiation."""
        service = WeightScaleService()
        assert service is not None
