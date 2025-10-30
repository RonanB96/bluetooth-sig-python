"""Tests for LN Feature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LNFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.ln_feature import LNFeatureData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLNFeatureCharacteristic(CommonCharacteristicTests):
    """Test suite for LN Feature characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
    Only adds LN feature-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> LNFeatureCharacteristic:
        """Return a LN Feature characteristic instance."""
        return LNFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for LN Feature characteristic."""
        return "2A6A"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Return valid test data for LN feature (basic features enabled)."""
        # Features bitmap with some basic features enabled
        features_bitmap = 0x0000001F  # Instantaneous speed, total distance, location, elevation, heading
        return CharacteristicTestData(
            input_data=bytearray(features_bitmap.to_bytes(4, byteorder="little")),
            expected_value=LNFeatureData(
                features_bitmap=features_bitmap,
                instantaneous_speed_supported=True,
                total_distance_supported=True,
                location_supported=True,
                elevation_supported=True,
                heading_supported=True,
                rolling_time_supported=False,
                utc_time_supported=False,
                remaining_distance_supported=False,
                remaining_vertical_distance_supported=False,
                estimated_time_of_arrival_supported=False,
                number_of_beacons_in_solution_supported=False,
                number_of_beacons_in_view_supported=False,
                time_to_first_fix_supported=False,
                estimated_horizontal_position_error_supported=False,
                estimated_vertical_position_error_supported=False,
                horizontal_dilution_of_precision_supported=False,
                vertical_dilution_of_precision_supported=False,
                location_and_speed_characteristic_content_masking_supported=False,
                fix_rate_setting_supported=False,
                elevation_setting_supported=False,
                position_status_supported=False,
            ),
            description="LN Feature with basic features enabled",
        )

    # === LN Feature-Specific Tests ===
    @pytest.mark.parametrize(
        "features_bitmap,expected_features",
        [
            # Basic features (bits 0-4)
            (
                0x0000001F,  # Instantaneous speed, total distance, location, elevation, heading
                {
                    "instantaneous_speed_supported": True,
                    "total_distance_supported": True,
                    "location_supported": True,
                    "elevation_supported": True,
                    "heading_supported": True,
                    "rolling_time_supported": False,
                    "utc_time_supported": False,
                    "remaining_distance_supported": False,
                    "remaining_vertical_distance_supported": False,
                    "estimated_time_of_arrival_supported": False,
                    "number_of_beacons_in_solution_supported": False,
                    "number_of_beacons_in_view_supported": False,
                    "time_to_first_fix_supported": False,
                    "estimated_horizontal_position_error_supported": False,
                    "estimated_vertical_position_error_supported": False,
                    "horizontal_dilution_of_precision_supported": False,
                    "vertical_dilution_of_precision_supported": False,
                    "location_and_speed_characteristic_content_masking_supported": False,
                    "fix_rate_setting_supported": False,
                    "elevation_setting_supported": False,
                    "position_status_supported": False,
                },
            ),
            # Advanced features (bits 5-11)
            (
                0x00000FE0,  # Rolling time, UTC time, remaining distance, remaining vertical distance,
                # ETA, beacons in solution, beacons in view
                {
                    "instantaneous_speed_supported": False,
                    "total_distance_supported": False,
                    "location_supported": False,
                    "elevation_supported": False,
                    "heading_supported": False,
                    "rolling_time_supported": True,
                    "utc_time_supported": True,
                    "remaining_distance_supported": True,
                    "remaining_vertical_distance_supported": True,
                    "estimated_time_of_arrival_supported": True,
                    "number_of_beacons_in_solution_supported": True,
                    "number_of_beacons_in_view_supported": True,
                    "time_to_first_fix_supported": False,
                    "estimated_horizontal_position_error_supported": False,
                    "estimated_vertical_position_error_supported": False,
                    "horizontal_dilution_of_precision_supported": False,
                    "vertical_dilution_of_precision_supported": False,
                    "location_and_speed_characteristic_content_masking_supported": False,
                    "fix_rate_setting_supported": False,
                    "elevation_setting_supported": False,
                    "position_status_supported": False,
                },
            ),
            # Positioning features (bits 12-16)
            (
                0x0001F000,  # Time to first fix, horizontal error, vertical error, HDOP, VDOP
                {
                    "instantaneous_speed_supported": False,
                    "total_distance_supported": False,
                    "location_supported": False,
                    "elevation_supported": False,
                    "heading_supported": False,
                    "rolling_time_supported": False,
                    "utc_time_supported": False,
                    "remaining_distance_supported": False,
                    "remaining_vertical_distance_supported": False,
                    "estimated_time_of_arrival_supported": False,
                    "number_of_beacons_in_solution_supported": False,
                    "number_of_beacons_in_view_supported": False,
                    "time_to_first_fix_supported": True,
                    "estimated_horizontal_position_error_supported": True,
                    "estimated_vertical_position_error_supported": True,
                    "horizontal_dilution_of_precision_supported": True,
                    "vertical_dilution_of_precision_supported": True,
                    "location_and_speed_characteristic_content_masking_supported": False,
                    "fix_rate_setting_supported": False,
                    "elevation_setting_supported": False,
                    "position_status_supported": False,
                },
            ),
            # Settings features (bits 17-20)
            (
                0x001E0000,  # Content masking, fix rate, elevation setting, position status
                {
                    "instantaneous_speed_supported": False,
                    "total_distance_supported": False,
                    "location_supported": False,
                    "elevation_supported": False,
                    "heading_supported": False,
                    "rolling_time_supported": False,
                    "utc_time_supported": False,
                    "remaining_distance_supported": False,
                    "remaining_vertical_distance_supported": False,
                    "estimated_time_of_arrival_supported": False,
                    "number_of_beacons_in_solution_supported": False,
                    "number_of_beacons_in_view_supported": False,
                    "time_to_first_fix_supported": False,
                    "estimated_horizontal_position_error_supported": False,
                    "estimated_vertical_position_error_supported": False,
                    "horizontal_dilution_of_precision_supported": False,
                    "vertical_dilution_of_precision_supported": False,
                    "location_and_speed_characteristic_content_masking_supported": True,
                    "fix_rate_setting_supported": True,
                    "elevation_setting_supported": True,
                    "position_status_supported": True,
                },
            ),
        ],
    )
    def test_ln_feature_various_combinations(
        self, characteristic: LNFeatureCharacteristic, features_bitmap: int, expected_features: dict[str, bool]
    ) -> None:
        """Test LN feature with various feature combinations."""
        data = bytearray(features_bitmap.to_bytes(4, byteorder="little"))

        result = characteristic.decode_value(data)
        assert result.features_bitmap == features_bitmap
        for field, expected in expected_features.items():
            assert getattr(result, field) == expected, f"Field {field} should be {expected}"

    def test_ln_feature_all_features_enabled(self, characteristic: LNFeatureCharacteristic) -> None:
        """Test LN feature with all features enabled."""
        # All features enabled (32-bit max value)
        features_bitmap = 0xFFFFFFFF
        data = bytearray(features_bitmap.to_bytes(4, byteorder="little"))

        result = characteristic.decode_value(data)
        assert result.features_bitmap == features_bitmap
        # Check that all boolean features are True
        feature_fields = [field for field in dir(result) if field.endswith("_supported") and not field.startswith("_")]
        for field in feature_fields:
            assert getattr(result, field) is True, f"Field {field} should be True for all features enabled"

    def test_ln_feature_no_features_enabled(self, characteristic: LNFeatureCharacteristic) -> None:
        """Test LN feature with no features enabled."""
        # No features enabled
        features_bitmap = 0x00000000
        data = bytearray(features_bitmap.to_bytes(4, byteorder="little"))

        result = characteristic.decode_value(data)
        assert result.features_bitmap == features_bitmap
        # Check that all boolean features are False
        feature_fields = [field for field in dir(result) if field.endswith("_supported") and not field.startswith("_")]
        for field in feature_fields:
            assert getattr(result, field) is False, f"Field {field} should be False for no features enabled"
