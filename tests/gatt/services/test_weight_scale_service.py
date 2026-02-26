"""Tests for Weight Scale Service and related characteristics."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.registry import CharacteristicName
from bluetooth_sig.gatt.characteristics.weight_measurement import WeightMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.weight_scale_feature import (
    WeightMeasurementResolution,
    WeightScaleFeatureCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.gatt.services.weight_scale import WeightScaleService
from bluetooth_sig.types.units import MeasurementSystem, WeightUnit


class TestWeightMeasurementCharacteristic:
    """Test Weight Measurement characteristic implementation."""

    def test_characteristic_name(self) -> None:
        """Test characteristic name resolution."""
        char = WeightMeasurementCharacteristic()
        assert char._characteristic_name == "Weight Measurement"
        # Auto-resolved from BaseCharacteristic[WeightMeasurementData]
        from bluetooth_sig.gatt.characteristics.weight_measurement import WeightMeasurementData

        assert char.python_type is WeightMeasurementData

    def test_parse_basic_weight_metric(self) -> None:
        """Test parsing basic weight in metric units."""
        char = WeightMeasurementCharacteristic()

        # Flags: 0x00 (metric units), Weight: 14000 (70.00 kg with 0.005 kg resolution)
        data = bytearray([0x00, 0x70, 0x36])  # 0x3670 = 13936
        result = char.parse_value(data)

        assert hasattr(result, "weight")
        assert result.weight == pytest.approx(69.68, abs=0.01)  # 13936 * 0.005
        assert result.weight_unit == WeightUnit.KG
        assert result.measurement_units == MeasurementSystem.METRIC

    def test_parse_basic_weight_imperial(self) -> None:
        """Test parsing basic weight in imperial units."""
        char = WeightMeasurementCharacteristic()

        # Flags: 0x01 (imperial units), Weight: 15000
        # (150.00 lb with 0.01 lb resolution)
        data = bytearray([0x01, 0x98, 0x3A])  # 0x3A98 = 15000
        result = char.parse_value(data)

        assert hasattr(result, "weight")
        assert result.weight == pytest.approx(150.0, abs=0.01)  # 15000 * 0.01
        assert result.weight_unit == WeightUnit.LB
        assert result.measurement_units == MeasurementSystem.IMPERIAL

    def test_parse_weight_with_user_id(self) -> None:
        """Test parsing weight with user ID."""
        char = WeightMeasurementCharacteristic()

        # Flags: 0x04 (user ID present), Weight: 14000, User ID: 5
        data = bytearray([0x04, 0x70, 0x36, 0x05])
        result = char.parse_value(data)

        assert hasattr(result, "weight")
        assert hasattr(result, "user_id")
        assert result.user_id == 5

    def test_parse_invalid_data(self) -> None:
        """Test parsing with invalid data."""
        char = WeightMeasurementCharacteristic()

        # Too short data
        with pytest.raises(CharacteristicParseError, match="at least 3 bytes"):
            char.parse_value(bytearray([0x00, 0x70]))

    def test_unit_property(self) -> None:
        """Test unit property."""
        char = WeightMeasurementCharacteristic()
        assert char.unit == "kg"


class TestWeightScaleFeatureCharacteristic:
    """Test Weight Scale Feature characteristic implementation."""

    def test_characteristic_name(self) -> None:
        """Test characteristic name resolution."""
        char = WeightScaleFeatureCharacteristic()
        assert char._characteristic_name == "Weight Scale Feature"
        from bluetooth_sig.gatt.characteristics.weight_scale_feature import WeightScaleFeatureData

        assert char.python_type is WeightScaleFeatureData

    def test_parse_basic_features(self) -> None:
        """Test parsing basic feature flags."""
        char = WeightScaleFeatureCharacteristic()

        # Features: 0x0000000F (timestamp, multiple users, BMI supported,
        # weight resolution 1)
        data = bytearray([0x0F, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result.timestamp_supported is True
        assert result.multiple_users_supported is True
        assert result.bmi_supported is True
        assert result.weight_measurement_resolution == WeightMeasurementResolution.HALF_KG_OR_1_LB

    def test_parse_no_features(self) -> None:
        """Test parsing with no features enabled."""
        char = WeightScaleFeatureCharacteristic()

        # Features: 0x00000000 (no features)
        data = bytearray([0x00, 0x00, 0x00, 0x00])
        result = char.parse_value(data)

        assert result.timestamp_supported is False
        assert result.multiple_users_supported is False
        assert result.bmi_supported is False
        assert result.weight_measurement_resolution == WeightMeasurementResolution.NOT_SPECIFIED

    def test_parse_invalid_data(self) -> None:
        """Test parsing with invalid data."""
        char = WeightScaleFeatureCharacteristic()

        # Too short data
        with pytest.raises(CharacteristicParseError, match="at least 4 bytes"):
            char.parse_value(bytearray([0x00, 0x00, 0x00]))

    def test_unit_property(self) -> None:
        """Test unit property (should be empty for feature characteristic)."""
        char = WeightScaleFeatureCharacteristic()
        assert char.unit == ""


class TestWeightScaleService:
    """Test Weight Scale Service implementation."""

    def test_expected_characteristics(self) -> None:
        """Test expected characteristics for the service."""
        expected = WeightScaleService.get_expected_characteristics()

        assert CharacteristicName.WEIGHT_MEASUREMENT in expected
        assert CharacteristicName.WEIGHT_SCALE_FEATURE in expected
        assert expected[CharacteristicName.WEIGHT_MEASUREMENT].char_class == WeightMeasurementCharacteristic
        assert expected[CharacteristicName.WEIGHT_SCALE_FEATURE].char_class == WeightScaleFeatureCharacteristic

    def test_required_characteristics(self) -> None:
        """Test required characteristics for the service."""
        required = WeightScaleService.get_required_characteristics()

        assert CharacteristicName.WEIGHT_MEASUREMENT in required
        assert required[CharacteristicName.WEIGHT_MEASUREMENT].char_class == WeightMeasurementCharacteristic
        # Weight Scale Feature is not required

    def test_service_creation(self) -> None:
        """Test service instantiation."""
        service = WeightScaleService()
        assert service is not None
