"""Test glucose feature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GlucoseFeatureCharacteristic, GlucoseFeatures
from bluetooth_sig.gatt.characteristics.glucose_feature import GlucoseFeatureData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGlucoseFeatureCharacteristic(CommonCharacteristicTests):
    """Test Glucose Feature characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> GlucoseFeatureCharacteristic:
        """Fixture providing a glucose feature characteristic."""
        return GlucoseFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for glucose feature characteristic."""
        return "2A51"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for glucose feature characteristic."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x04]),  # 0x0403: Low Battery + Sensor Malfunction + Multiple Bond
                expected_value=GlucoseFeatureData(
                    features_bitmap=(
                        GlucoseFeatures.LOW_BATTERY_DETECTION
                        | GlucoseFeatures.SENSOR_MALFUNCTION_DETECTION
                        | GlucoseFeatures.MULTIPLE_BOND_SUPPORT
                    ),
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
                ),
                description="Multiple glucose features enabled",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),  # 0x0001: Only Low Battery Detection
                expected_value=GlucoseFeatureData(
                    features_bitmap=GlucoseFeatures.LOW_BATTERY_DETECTION,
                    low_battery_detection=True,
                    sensor_malfunction_detection=False,
                    sensor_sample_size=False,
                    sensor_strip_insertion_error=False,
                    sensor_strip_type_error=False,
                    sensor_result_high_low=False,
                    sensor_temperature_high_low=False,
                    sensor_read_interrupt=False,
                    general_device_fault=False,
                    time_fault=False,
                    multiple_bond_support=False,
                    enabled_features=(GlucoseFeatures.LOW_BATTERY_DETECTION,),
                    feature_count=1,
                ),
                description="Only low battery detection enabled",
            ),
        ]

    def test_glucose_feature_basic_parsing(
        self, characteristic: GlucoseFeatureCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test basic glucose feature data parsing."""
        test_data = valid_test_data[0].input_data

        result = characteristic.decode_value(test_data)
        assert result.features_bitmap == GlucoseFeatures(0x0403)
        assert result.low_battery_detection is True
        assert result.sensor_malfunction_detection is True
        assert result.multiple_bond_support is True
        assert result.feature_count == 3

    def test_glucose_feature_all_features_disabled(self, characteristic: GlucoseFeatureCharacteristic) -> None:
        """Test glucose feature with all features disabled."""
        test_data = bytearray([0x00, 0x00])

        result = characteristic.decode_value(test_data)
        assert result.features_bitmap == GlucoseFeatures(0x0000)
        assert result.low_battery_detection is False
        assert result.sensor_malfunction_detection is False
        assert result.multiple_bond_support is False
        assert result.feature_count == 0

    def test_glucose_feature_descriptions(self, characteristic: GlucoseFeatureCharacteristic) -> None:
        """Test feature bit descriptions."""
        assert "Low Battery Detection During Measurement Supported" in characteristic.get_feature_description(
            GlucoseFeatures.LOW_BATTERY_DETECTION.value
        )
        assert "Multiple Bond Supported" in characteristic.get_feature_description(
            GlucoseFeatures.MULTIPLE_BOND_SUPPORT.value
        )
        assert "Reserved feature" in characteristic.get_feature_description(15)

    def test_glucose_feature_invalid_data(self, characteristic: GlucoseFeatureCharacteristic) -> None:
        """Test glucose feature with invalid data."""
        with pytest.raises(ValueError, match="must be at least 2 bytes"):
            characteristic.decode_value(bytearray([0x00]))

    def test_glucose_feature_encode_value(self, characteristic: GlucoseFeatureCharacteristic) -> None:
        """Test encoding GlucoseFeatureData back to bytes."""
        from bluetooth_sig.gatt.characteristics.glucose_feature import GlucoseFeatureData

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
        encoded = characteristic.encode_value(test_data)

        # Should produce the correct bytes
        assert len(encoded) == 2
        assert encoded == bytearray([0x03, 0x04])  # Little endian 0x0403

    def test_glucose_feature_round_trip(self, characteristic: GlucoseFeatureCharacteristic) -> None:
        """Test that parsing and encoding preserve data."""
        # Test with basic features
        original_data = bytearray([0x03, 0x04])  # Low Battery + Sensor Malfunction + Multiple Bond

        # Parse the data
        parsed = characteristic.decode_value(original_data)

        # Encode it back
        encoded = characteristic.encode_value(parsed)

        # Should match the original
        assert encoded == original_data
