"""Weight Scale Feature characteristic implementation."""

from __future__ import annotations

from enum import IntEnum, IntFlag
from typing import Any

import msgspec

from .base import BaseCharacteristic
from .utils import BitFieldUtils, DataParser


class WeightScaleBits:
    # pylint: disable=missing-class-docstring,too-few-public-methods

    # Weight Scale Feature bit field constants
    WEIGHT_RESOLUTION_START_BIT = 3  # Weight measurement resolution starts at bit 3
    WEIGHT_RESOLUTION_BIT_WIDTH = 4  # Weight measurement resolution uses 4 bits
    HEIGHT_RESOLUTION_START_BIT = 7  # Height measurement resolution starts at bit 7
    HEIGHT_RESOLUTION_BIT_WIDTH = 3  # Height measurement resolution uses 3 bits


class WeightScaleFeatures(IntFlag):
    """Weight Scale Feature flags as per Bluetooth SIG specification."""

    TIMESTAMP_SUPPORTED = 0x01
    MULTIPLE_USERS_SUPPORTED = 0x02
    BMI_SUPPORTED = 0x04


class WeightMeasurementResolution(IntEnum):
    """Weight measurement resolution enumeration."""

    NOT_SPECIFIED = 0
    HALF_KG_OR_1_LB = 1
    POINT_2_KG_OR_HALF_LB = 2
    POINT_1_KG_OR_POINT_2_LB = 3
    POINT_05_KG_OR_POINT_1_LB = 4
    POINT_02_KG_OR_POINT_05_LB = 5
    POINT_01_KG_OR_POINT_02_LB = 6
    POINT_005_KG_OR_POINT_01_LB = 7

    def __str__(self) -> str:
        descriptions = {
            0: "not_specified",
            1: "0.5_kg_or_1_lb",
            2: "0.2_kg_or_0.5_lb",
            3: "0.1_kg_or_0.2_lb",
            4: "0.05_kg_or_0.1_lb",
            5: "0.02_kg_or_0.05_lb",
            6: "0.01_kg_or_0.02_lb",
            7: "0.005_kg_or_0.01_lb",
        }
        return descriptions.get(self.value, "Reserved for Future Use")


class HeightMeasurementResolution(IntEnum):
    """Height measurement resolution enumeration."""

    NOT_SPECIFIED = 0
    POINT_01_M_OR_1_INCH = 1
    POINT_005_M_OR_HALF_INCH = 2
    POINT_001_M_OR_POINT_1_INCH = 3

    def __str__(self) -> str:
        descriptions = {
            0: "not_specified",
            1: "0.01_m_or_1_inch",
            2: "0.005_m_or_0.5_inch",
            3: "0.001_m_or_0.1_inch",
        }
        return descriptions.get(self.value, "Reserved for Future Use")


class WeightScaleFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Weight Scale Feature characteristic."""

    raw_value: int
    timestamp_supported: bool
    multiple_users_supported: bool
    bmi_supported: bool
    weight_measurement_resolution: WeightMeasurementResolution
    height_measurement_resolution: HeightMeasurementResolution

    def __post_init__(self) -> None:
        """Validate weight scale feature data."""
        if not 0 <= self.raw_value <= 0xFFFFFFFF:
            raise ValueError("Raw value must be a 32-bit unsigned integer")


class WeightScaleFeatureCharacteristic(BaseCharacteristic):
    """Weight Scale Feature characteristic (0x2A9E).

    Used to indicate which optional features are supported by the weight
    scale. This is a read-only characteristic that describes device
    capabilities.
    """

    _characteristic_name: str = "Weight Scale Feature"

    min_length: int = 4  # Features(4) fixed length
    max_length: int = 4  # Features(4) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> WeightScaleFeatureData:
        """Parse weight scale feature data according to Bluetooth
        specification.

        Format: Features(4 bytes) - bitmask indicating supported features

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            WeightScaleFeatureData containing parsed feature flags

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("Weight Scale Feature data must be at least 4 bytes")

        features_raw = DataParser.parse_int32(data, 0, signed=False)

        # Parse feature flags according to specification
        return WeightScaleFeatureData(
            raw_value=features_raw,
            timestamp_supported=bool(features_raw & WeightScaleFeatures.TIMESTAMP_SUPPORTED),
            multiple_users_supported=bool(features_raw & WeightScaleFeatures.MULTIPLE_USERS_SUPPORTED),
            bmi_supported=bool(features_raw & WeightScaleFeatures.BMI_SUPPORTED),
            weight_measurement_resolution=self._get_weight_resolution(features_raw),
            height_measurement_resolution=self._get_height_resolution(features_raw),
        )

    def encode_value(self, data: WeightScaleFeatureData) -> bytearray:
        """Encode weight scale feature value back to bytes.

        Args:
            data: WeightScaleFeatureData with feature flags

        Returns:
            Encoded bytes representing the weight scale features (uint32)
        """
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.timestamp_supported:
            features_bitmap |= WeightScaleFeatures.TIMESTAMP_SUPPORTED
        if data.multiple_users_supported:
            features_bitmap |= WeightScaleFeatures.MULTIPLE_USERS_SUPPORTED
        if data.bmi_supported:
            features_bitmap |= WeightScaleFeatures.BMI_SUPPORTED

        # Add resolution bits using bit field utilities
        features_bitmap = BitFieldUtils.set_bit_field(
            features_bitmap,
            data.weight_measurement_resolution.value,
            WeightScaleBits.WEIGHT_RESOLUTION_START_BIT,
            WeightScaleBits.WEIGHT_RESOLUTION_BIT_WIDTH,
        )
        features_bitmap = BitFieldUtils.set_bit_field(
            features_bitmap,
            data.height_measurement_resolution.value,
            WeightScaleBits.HEIGHT_RESOLUTION_START_BIT,
            WeightScaleBits.HEIGHT_RESOLUTION_BIT_WIDTH,
        )

        return bytearray(DataParser.encode_int32(features_bitmap, signed=False))

    def _get_weight_resolution(self, features: int) -> WeightMeasurementResolution:
        """Extract weight measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            WeightMeasurementResolution enum value
        """
        resolution_bits = BitFieldUtils.extract_bit_field(
            features,
            WeightScaleBits.WEIGHT_RESOLUTION_START_BIT,
            WeightScaleBits.WEIGHT_RESOLUTION_BIT_WIDTH,
        )
        try:
            return WeightMeasurementResolution(resolution_bits)
        except ValueError:
            return WeightMeasurementResolution.NOT_SPECIFIED

    def _get_height_resolution(self, features: int) -> HeightMeasurementResolution:
        """Extract height measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            HeightMeasurementResolution enum value
        """
        resolution_bits = BitFieldUtils.extract_bit_field(
            features,
            WeightScaleBits.HEIGHT_RESOLUTION_START_BIT,
            WeightScaleBits.HEIGHT_RESOLUTION_BIT_WIDTH,
        )
        try:
            return HeightMeasurementResolution(resolution_bits)
        except ValueError:
            return HeightMeasurementResolution.NOT_SPECIFIED
