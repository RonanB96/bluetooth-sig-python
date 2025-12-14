"""LN Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import ValueType
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class LNFeatures(IntFlag):
    """LN Feature flags as per Bluetooth SIG specification."""

    INSTANTANEOUS_SPEED_SUPPORTED = 0x0001
    TOTAL_DISTANCE_SUPPORTED = 0x0002
    LOCATION_SUPPORTED = 0x0004
    ELEVATION_SUPPORTED = 0x0008
    HEADING_SUPPORTED = 0x0010
    ROLLING_TIME_SUPPORTED = 0x0020
    UTC_TIME_SUPPORTED = 0x0040
    REMAINING_DISTANCE_SUPPORTED = 0x0080
    REMAINING_VERTICAL_DISTANCE_SUPPORTED = 0x0100
    ESTIMATED_TIME_OF_ARRIVAL_SUPPORTED = 0x0200
    NUMBER_OF_BEACONS_IN_SOLUTION_SUPPORTED = 0x0400
    NUMBER_OF_BEACONS_IN_VIEW_SUPPORTED = 0x0800
    TIME_TO_FIRST_FIX_SUPPORTED = 0x1000
    ESTIMATED_HORIZONTAL_POSITION_ERROR_SUPPORTED = 0x2000
    ESTIMATED_VERTICAL_POSITION_ERROR_SUPPORTED = 0x4000
    HORIZONTAL_DILUTION_OF_PRECISION_SUPPORTED = 0x8000
    VERTICAL_DILUTION_OF_PRECISION_SUPPORTED = 0x00010000
    LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT_MASKING_SUPPORTED = 0x00020000
    FIX_RATE_SETTING_SUPPORTED = 0x00040000
    ELEVATION_SETTING_SUPPORTED = 0x00080000
    POSITION_STATUS_SUPPORTED = 0x00100000


class LNFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from LN Feature characteristic."""

    features_bitmap: int
    instantaneous_speed_supported: bool
    total_distance_supported: bool
    location_supported: bool
    elevation_supported: bool
    heading_supported: bool
    rolling_time_supported: bool
    utc_time_supported: bool
    remaining_distance_supported: bool
    remaining_vertical_distance_supported: bool
    estimated_time_of_arrival_supported: bool
    number_of_beacons_in_solution_supported: bool
    number_of_beacons_in_view_supported: bool
    time_to_first_fix_supported: bool
    estimated_horizontal_position_error_supported: bool
    estimated_vertical_position_error_supported: bool
    horizontal_dilution_of_precision_supported: bool
    vertical_dilution_of_precision_supported: bool
    location_and_speed_characteristic_content_masking_supported: bool
    fix_rate_setting_supported: bool
    elevation_setting_supported: bool
    position_status_supported: bool


class LNFeatureCharacteristic(BaseCharacteristic):
    """LN Feature characteristic.

    Used to represent the supported features of a location and navigation sensor.
    """

    min_length = 4
    _manual_value_type: ValueType | str | None = ValueType.DICT  # Override since decode_value returns dataclass

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> LNFeatureData:
        """Parse LN feature data according to Bluetooth specification.

        Format: Features(4) - 32-bit bitmap indicating supported features.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            LNFeatureData containing parsed feature bitmap and capabilities.

        """
        if len(data) < 4:
            raise ValueError("LN Feature data must be at least 4 bytes")

        features_bitmap = DataParser.parse_int32(data, 0, signed=False)

        # Extract individual feature flags
        features = {
            "instantaneous_speed_supported": bool(features_bitmap & LNFeatures.INSTANTANEOUS_SPEED_SUPPORTED),
            "total_distance_supported": bool(features_bitmap & LNFeatures.TOTAL_DISTANCE_SUPPORTED),
            "location_supported": bool(features_bitmap & LNFeatures.LOCATION_SUPPORTED),
            "elevation_supported": bool(features_bitmap & LNFeatures.ELEVATION_SUPPORTED),
            "heading_supported": bool(features_bitmap & LNFeatures.HEADING_SUPPORTED),
            "rolling_time_supported": bool(features_bitmap & LNFeatures.ROLLING_TIME_SUPPORTED),
            "utc_time_supported": bool(features_bitmap & LNFeatures.UTC_TIME_SUPPORTED),
            "remaining_distance_supported": bool(features_bitmap & LNFeatures.REMAINING_DISTANCE_SUPPORTED),
            "remaining_vertical_distance_supported": bool(
                features_bitmap & LNFeatures.REMAINING_VERTICAL_DISTANCE_SUPPORTED
            ),
            "estimated_time_of_arrival_supported": bool(
                features_bitmap & LNFeatures.ESTIMATED_TIME_OF_ARRIVAL_SUPPORTED
            ),
            "number_of_beacons_in_solution_supported": bool(
                features_bitmap & LNFeatures.NUMBER_OF_BEACONS_IN_SOLUTION_SUPPORTED
            ),
            "number_of_beacons_in_view_supported": bool(
                features_bitmap & LNFeatures.NUMBER_OF_BEACONS_IN_VIEW_SUPPORTED
            ),
            "time_to_first_fix_supported": bool(features_bitmap & LNFeatures.TIME_TO_FIRST_FIX_SUPPORTED),
            "estimated_horizontal_position_error_supported": bool(
                features_bitmap & LNFeatures.ESTIMATED_HORIZONTAL_POSITION_ERROR_SUPPORTED
            ),
            "estimated_vertical_position_error_supported": bool(
                features_bitmap & LNFeatures.ESTIMATED_VERTICAL_POSITION_ERROR_SUPPORTED
            ),
            "horizontal_dilution_of_precision_supported": bool(
                features_bitmap & LNFeatures.HORIZONTAL_DILUTION_OF_PRECISION_SUPPORTED
            ),
            "vertical_dilution_of_precision_supported": bool(
                features_bitmap & LNFeatures.VERTICAL_DILUTION_OF_PRECISION_SUPPORTED
            ),
            "location_and_speed_characteristic_content_masking_supported": bool(
                features_bitmap & LNFeatures.LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT_MASKING_SUPPORTED
            ),
            "fix_rate_setting_supported": bool(features_bitmap & LNFeatures.FIX_RATE_SETTING_SUPPORTED),
            "elevation_setting_supported": bool(features_bitmap & LNFeatures.ELEVATION_SETTING_SUPPORTED),
            "position_status_supported": bool(features_bitmap & LNFeatures.POSITION_STATUS_SUPPORTED),
        }

        return LNFeatureData(features_bitmap=features_bitmap, **features)

    def encode_value(self, data: LNFeatureData) -> bytearray:
        """Encode LNFeatureData back to bytes.

        Args:
            data: LNFeatureData instance to encode

        Returns:
            Encoded bytes representing the LN features

        """
        return DataParser.encode_int32(data.features_bitmap, signed=False)
