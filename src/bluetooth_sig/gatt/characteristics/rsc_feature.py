"""RSC Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RSCFeatures(IntFlag):
    """RSC Feature flags as per Bluetooth SIG specification."""

    INSTANTANEOUS_STRIDE_LENGTH_SUPPORTED = 0x01
    TOTAL_DISTANCE_SUPPORTED = 0x02
    WALKING_OR_RUNNING_STATUS_SUPPORTED = 0x04
    CALIBRATION_PROCEDURE_SUPPORTED = 0x08
    MULTIPLE_SENSOR_LOCATIONS_SUPPORTED = 0x10


class RSCFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from RSC Feature characteristic."""

    features: RSCFeatures
    instantaneous_stride_length_supported: bool
    total_distance_supported: bool
    walking_or_running_status_supported: bool
    calibration_procedure_supported: bool
    multiple_sensor_locations_supported: bool


class RSCFeatureCharacteristic(BaseCharacteristic[RSCFeatureData]):
    """RSC Feature characteristic (0x2A54).

    Used to expose the supported features of an RSC sensor.
    Contains a 16-bit bitmask indicating supported measurement
    capabilities.
    """

    expected_length: int = 2

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> RSCFeatureData:
        """Parse RSC feature data.

        Format: 16-bit feature bitmask (little endian).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            RSCFeatureData containing parsed feature flags.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 2:
            raise ValueError("RSC Feature data must be at least 2 bytes")

        # Parse 16-bit unsigned integer (little endian)
        feature_mask: int = DataParser.parse_int16(data, 0, signed=False)

        # Parse feature flags according to specification
        return RSCFeatureData(
            features=RSCFeatures(feature_mask),
            instantaneous_stride_length_supported=bool(
                feature_mask & RSCFeatures.INSTANTANEOUS_STRIDE_LENGTH_SUPPORTED
            ),
            total_distance_supported=bool(feature_mask & RSCFeatures.TOTAL_DISTANCE_SUPPORTED),
            walking_or_running_status_supported=bool(feature_mask & RSCFeatures.WALKING_OR_RUNNING_STATUS_SUPPORTED),
            calibration_procedure_supported=bool(feature_mask & RSCFeatures.CALIBRATION_PROCEDURE_SUPPORTED),
            multiple_sensor_locations_supported=bool(feature_mask & RSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED),
        )

    def _encode_value(self, data: RSCFeatureData) -> bytearray:
        """Encode RSC feature value back to bytes.

        Args:
            data: RSCFeatureData containing RSC feature data

        Returns:
            Encoded bytes representing the RSC features (uint16)

        """
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.instantaneous_stride_length_supported:
            features_bitmap |= RSCFeatures.INSTANTANEOUS_STRIDE_LENGTH_SUPPORTED
        if data.total_distance_supported:
            features_bitmap |= RSCFeatures.TOTAL_DISTANCE_SUPPORTED
        if data.walking_or_running_status_supported:
            features_bitmap |= RSCFeatures.WALKING_OR_RUNNING_STATUS_SUPPORTED
        if data.calibration_procedure_supported:
            features_bitmap |= RSCFeatures.CALIBRATION_PROCEDURE_SUPPORTED
        if data.multiple_sensor_locations_supported:
            features_bitmap |= RSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED

        return DataParser.encode_int16(features_bitmap, signed=False)
