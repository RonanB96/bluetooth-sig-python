"""Glucose Feature characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Any

from .base import BaseCharacteristic
from .utils import BitFieldUtils, DataParser


class GlucoseFeatures(IntFlag):
    """Glucose Feature flags according to Bluetooth SIG specification."""

    LOW_BATTERY_DETECTION = 0x0001
    SENSOR_MALFUNCTION_DETECTION = 0x0002
    SENSOR_SAMPLE_SIZE = 0x0004
    SENSOR_STRIP_INSERTION_ERROR = 0x0008
    SENSOR_STRIP_TYPE_ERROR = 0x0010
    SENSOR_RESULT_HIGH_LOW = 0x0020
    SENSOR_TEMPERATURE_HIGH_LOW = 0x0040
    SENSOR_READ_INTERRUPT = 0x0080
    GENERAL_DEVICE_FAULT = 0x0100
    TIME_FAULT = 0x0200
    MULTIPLE_BOND_SUPPORT = 0x0400

    @classmethod
    def get_description(cls, feature: GlucoseFeatures) -> str:
        """Get human-readable description for a feature."""
        descriptions = {
            cls.LOW_BATTERY_DETECTION: "Low Battery Detection During Measurement Supported",
            cls.SENSOR_MALFUNCTION_DETECTION: "Sensor Malfunction Detection Supported",
            cls.SENSOR_SAMPLE_SIZE: "Sensor Sample Size Supported",
            cls.SENSOR_STRIP_INSERTION_ERROR: "Sensor Strip Insertion Error Detection Supported",
            cls.SENSOR_STRIP_TYPE_ERROR: "Sensor Strip Type Error Detection Supported",
            cls.SENSOR_RESULT_HIGH_LOW: "Sensor Result High-Low Detection Supported",
            cls.SENSOR_TEMPERATURE_HIGH_LOW: "Sensor Temperature High-Low Detection Supported",
            cls.SENSOR_READ_INTERRUPT: "Sensor Read Interrupt Detection Supported",
            cls.GENERAL_DEVICE_FAULT: "General Device Fault Supported",
            cls.TIME_FAULT: "Time Fault Supported",
            cls.MULTIPLE_BOND_SUPPORT: "Multiple Bond Supported",
        }
        return descriptions.get(feature, f"Reserved feature bit {feature.value:04x}")

    def get_enabled_features(self) -> list[str]:
        """Get list of human-readable enabled features."""
        enabled = []
        for feature in GlucoseFeatures:
            if self & feature:
                enabled.append(self.get_description(feature))
        return enabled


@dataclass
class GlucoseFeatureData:  # pylint: disable=too-many-instance-attributes
    """Parsed data from Glucose Feature characteristic."""

    features_bitmap: int
    low_battery_detection: bool
    sensor_malfunction_detection: bool
    sensor_sample_size: bool
    sensor_strip_insertion_error: bool
    sensor_strip_type_error: bool
    sensor_result_high_low: bool
    sensor_temperature_high_low: bool
    sensor_read_interrupt: bool
    general_device_fault: bool
    time_fault: bool
    multiple_bond_support: bool
    enabled_features: list[str]
    feature_count: int


@dataclass
class GlucoseFeatureCharacteristic(BaseCharacteristic):
    """Glucose Feature characteristic (0x2A51).

    Used to expose the supported features of a glucose monitoring device.
    Indicates which optional fields and capabilities are available.
    """

    _characteristic_name: str = "Glucose Feature"

    min_length: int = 2  # Features(2) fixed length
    max_length: int = 2  # Features(2) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(  # pylint: disable=too-many-locals
        self, data: bytearray, ctx: Any | None = None
    ) -> GlucoseFeatureData:
        """Parse glucose feature data according to Bluetooth specification.

        Format: Features(2) - 16-bit bitmap indicating supported features

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context information

        Returns:
            GlucoseFeatureData containing parsed feature bitmap and details

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Glucose Feature data must be at least 2 bytes")

        features_bitmap = DataParser.parse_int16(data, 0, signed=False)
        features = GlucoseFeatures(features_bitmap)

        # Extract individual feature flags using enum
        low_battery_detection = bool(features & GlucoseFeatures.LOW_BATTERY_DETECTION)
        sensor_malfunction_detection = bool(
            features & GlucoseFeatures.SENSOR_MALFUNCTION_DETECTION
        )
        sensor_sample_size = bool(features & GlucoseFeatures.SENSOR_SAMPLE_SIZE)
        sensor_strip_insertion_error = bool(
            features & GlucoseFeatures.SENSOR_STRIP_INSERTION_ERROR
        )
        sensor_strip_type_error = bool(
            features & GlucoseFeatures.SENSOR_STRIP_TYPE_ERROR
        )
        sensor_result_high_low = bool(features & GlucoseFeatures.SENSOR_RESULT_HIGH_LOW)
        sensor_temperature_high_low = bool(
            features & GlucoseFeatures.SENSOR_TEMPERATURE_HIGH_LOW
        )
        sensor_read_interrupt = bool(features & GlucoseFeatures.SENSOR_READ_INTERRUPT)
        general_device_fault = bool(features & GlucoseFeatures.GENERAL_DEVICE_FAULT)
        time_fault = bool(features & GlucoseFeatures.TIME_FAULT)
        multiple_bond_support = bool(features & GlucoseFeatures.MULTIPLE_BOND_SUPPORT)

        # Get enabled features using the enum method
        enabled_features = features.get_enabled_features()

        return GlucoseFeatureData(
            features_bitmap=features_bitmap,
            low_battery_detection=low_battery_detection,
            sensor_malfunction_detection=sensor_malfunction_detection,
            sensor_sample_size=sensor_sample_size,
            sensor_strip_insertion_error=sensor_strip_insertion_error,
            sensor_strip_type_error=sensor_strip_type_error,
            sensor_result_high_low=sensor_result_high_low,
            sensor_temperature_high_low=sensor_temperature_high_low,
            sensor_read_interrupt=sensor_read_interrupt,
            general_device_fault=general_device_fault,
            time_fault=time_fault,
            multiple_bond_support=multiple_bond_support,
            enabled_features=enabled_features,
            feature_count=len(enabled_features),
        )

    def encode_value(self, data: GlucoseFeatureData) -> bytearray:
        """Encode GlucoseFeatureData back to bytes.

        Args:
            data: GlucoseFeatureData instance to encode

        Returns:
            Encoded bytes representing the glucose features
        """
        # Reconstruct the features bitmap from individual flags using enum values
        features_bitmap = 0
        if data.low_battery_detection:
            features_bitmap |= GlucoseFeatures.LOW_BATTERY_DETECTION
        if data.sensor_malfunction_detection:
            features_bitmap |= GlucoseFeatures.SENSOR_MALFUNCTION_DETECTION
        if data.sensor_sample_size:
            features_bitmap |= GlucoseFeatures.SENSOR_SAMPLE_SIZE
        if data.sensor_strip_insertion_error:
            features_bitmap |= GlucoseFeatures.SENSOR_STRIP_INSERTION_ERROR
        if data.sensor_strip_type_error:
            features_bitmap |= GlucoseFeatures.SENSOR_STRIP_TYPE_ERROR
        if data.sensor_result_high_low:
            features_bitmap |= GlucoseFeatures.SENSOR_RESULT_HIGH_LOW
        if data.sensor_temperature_high_low:
            features_bitmap |= GlucoseFeatures.SENSOR_TEMPERATURE_HIGH_LOW
        if data.sensor_read_interrupt:
            features_bitmap |= GlucoseFeatures.SENSOR_READ_INTERRUPT
        if data.general_device_fault:
            features_bitmap |= GlucoseFeatures.GENERAL_DEVICE_FAULT
        if data.time_fault:
            features_bitmap |= GlucoseFeatures.TIME_FAULT
        if data.multiple_bond_support:
            features_bitmap |= GlucoseFeatures.MULTIPLE_BOND_SUPPORT

        # Pack as little-endian 16-bit integer
        return DataParser.encode_int16(features_bitmap, signed=False)

    def get_feature_description(self, feature_bit: int) -> str:
        """Get description for a specific feature bit.

        Args:
            feature_bit: Bit position (0-15)

        Returns:
            Human-readable description of the feature
        """
        # Convert bit position to feature flag value
        feature_value = BitFieldUtils.set_bit(0, feature_bit)
        try:
            feature = GlucoseFeatures(feature_value)
            return GlucoseFeatures.get_description(feature)
        except ValueError:
            return f"Reserved feature bit {feature_bit}"

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "bitmap"  # Feature bitmap
