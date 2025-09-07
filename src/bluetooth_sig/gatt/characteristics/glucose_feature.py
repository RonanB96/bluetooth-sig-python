"""Glucose Feature characteristic implementation."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


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

    def parse_value(self, data: bytearray) -> GlucoseFeatureData:
        """Parse glucose feature data according to Bluetooth specification.

        Format: Features(2) - 16-bit bitmap indicating supported features

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed feature bitmap and human-readable features

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Glucose Feature data must be at least 2 bytes")

        features = struct.unpack("<H", data[:2])[0]

        # Parse feature bitmap
        low_battery_detection = bool(features & 0x0001)
        sensor_malfunction_detection = bool(features & 0x0002)
        sensor_sample_size = bool(features & 0x0004)
        sensor_strip_insertion_error = bool(features & 0x0008)
        sensor_strip_type_error = bool(features & 0x0010)
        sensor_result_high_low = bool(features & 0x0020)
        sensor_temperature_high_low = bool(features & 0x0040)
        sensor_read_interrupt = bool(features & 0x0080)
        general_device_fault = bool(features & 0x0100)
        time_fault = bool(features & 0x0200)
        multiple_bond_support = bool(features & 0x0400)

        # Create human-readable summary
        enabled_features = []
        if low_battery_detection:
            enabled_features.append("Low Battery Detection")
        if sensor_malfunction_detection:
            enabled_features.append("Sensor Malfunction Detection")
        if sensor_sample_size:
            enabled_features.append("Sensor Sample Size")
        if sensor_strip_insertion_error:
            enabled_features.append("Sensor Strip Insertion Error")
        if sensor_strip_type_error:
            enabled_features.append("Sensor Strip Type Error")
        if sensor_result_high_low:
            enabled_features.append("Sensor Result High-Low Detection")
        if sensor_temperature_high_low:
            enabled_features.append("Sensor Temperature High-Low Detection")
        if sensor_read_interrupt:
            enabled_features.append("Sensor Read Interrupt Detection")
        if general_device_fault:
            enabled_features.append("General Device Fault")
        if time_fault:
            enabled_features.append("Time Fault")
        if multiple_bond_support:
            enabled_features.append("Multiple Bond Support")

        return GlucoseFeatureData(
            features_bitmap=features,
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
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.low_battery_detection:
            features_bitmap |= 0x0001
        if data.sensor_malfunction_detection:
            features_bitmap |= 0x0002
        if data.sensor_sample_size:
            features_bitmap |= 0x0004
        if data.sensor_strip_insertion_error:
            features_bitmap |= 0x0008
        if data.sensor_strip_type_error:
            features_bitmap |= 0x0010
        if data.sensor_result_high_low:
            features_bitmap |= 0x0020
        if data.sensor_temperature_high_low:
            features_bitmap |= 0x0040
        if data.sensor_read_interrupt:
            features_bitmap |= 0x0080
        if data.general_device_fault:
            features_bitmap |= 0x0100
        if data.time_fault:
            features_bitmap |= 0x0200
        if data.multiple_bond_support:
            features_bitmap |= 0x0400

        # Pack as little-endian 16-bit integer
        return bytearray(struct.pack("<H", features_bitmap))

    def get_feature_description(self, feature_bit: int) -> str:
        """Get description for a specific feature bit.

        Args:
            feature_bit: Bit position (0-15)

        Returns:
            Human-readable description of the feature
        """
        descriptions = {
            0: "Low Battery Detection During Measurement Supported",
            1: "Sensor Malfunction Detection Supported",
            2: "Sensor Sample Size Supported",
            3: "Sensor Strip Insertion Error Detection Supported",
            4: "Sensor Strip Type Error Detection Supported",
            5: "Sensor Result High-Low Detection Supported",
            6: "Sensor Temperature High-Low Detection Supported",
            7: "Sensor Read Interrupt Detection Supported",
            8: "General Device Fault Supported",
            9: "Time Fault Supported",
            10: "Multiple Bond Supported",
        }
        return descriptions.get(feature_bit, f"Reserved feature bit {feature_bit}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "bitmap"  # Feature bitmap
