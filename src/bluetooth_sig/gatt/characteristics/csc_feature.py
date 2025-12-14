"""CSC Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CSCFeatures(IntFlag):
    """CSC Feature flags as per Bluetooth SIG specification."""

    WHEEL_REVOLUTION_DATA_SUPPORTED = 0x01
    CRANK_REVOLUTION_DATA_SUPPORTED = 0x02
    MULTIPLE_SENSOR_LOCATIONS_SUPPORTED = 0x04


class CSCFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from CSC Feature characteristic."""

    features: CSCFeatures
    wheel_revolution_data_supported: bool
    crank_revolution_data_supported: bool
    multiple_sensor_locations_supported: bool


class CSCFeatureCharacteristic(BaseCharacteristic):
    """CSC Feature characteristic (0x2A5C).

    Used to expose the supported features of a CSC sensor.
    Contains a 16-bit bitmask indicating supported measurement
    capabilities.
    """

    expected_length: int = 2

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CSCFeatureData:
        """Parse CSC feature data.

        Format: 16-bit feature bitmask (little endian).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            CSCFeatureData containing parsed feature flags.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 2:
            raise ValueError("CSC Feature data must be at least 2 bytes")

        # Parse 16-bit unsigned integer (little endian)
        feature_mask: int = DataParser.parse_int16(data, 0, signed=False)

        # Parse feature flags according to specification
        return CSCFeatureData(
            features=CSCFeatures(feature_mask),
            wheel_revolution_data_supported=bool(feature_mask & CSCFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED),
            crank_revolution_data_supported=bool(feature_mask & CSCFeatures.CRANK_REVOLUTION_DATA_SUPPORTED),
            multiple_sensor_locations_supported=bool(feature_mask & CSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED),
        )

    def encode_value(self, data: CSCFeatureData) -> bytearray:
        """Encode CSC feature value back to bytes.

        Args:
            data: CSCFeatureData containing CSC feature data

        Returns:
            Encoded bytes representing the CSC features (uint16)

        """
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.wheel_revolution_data_supported:
            features_bitmap |= CSCFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
        if data.crank_revolution_data_supported:
            features_bitmap |= CSCFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
        if data.multiple_sensor_locations_supported:
            features_bitmap |= CSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED

        return DataParser.encode_int16(features_bitmap, signed=False)
