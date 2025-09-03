"""Glucose Feature characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class GlucoseFeatureCharacteristic(BaseCharacteristic):
    """Glucose Feature characteristic (0x2A51).

    Used to expose the supported features of a glucose monitoring device.
    Indicates which optional fields and capabilities are available.
    """

    _characteristic_name: str = "Glucose Feature"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, Any]:
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
        parsed_features = {
            "features_bitmap": features,
            "low_battery_detection": bool(features & 0x0001),
            "sensor_malfunction_detection": bool(features & 0x0002),
            "sensor_sample_size": bool(features & 0x0004),
            "sensor_strip_insertion_error": bool(features & 0x0008),
            "sensor_strip_type_error": bool(features & 0x0010),
            "sensor_result_high_low": bool(features & 0x0020),
            "sensor_temperature_high_low": bool(features & 0x0040),
            "sensor_read_interrupt": bool(features & 0x0080),
            "general_device_fault": bool(features & 0x0100),
            "time_fault": bool(features & 0x0200),
            "multiple_bond_support": bool(features & 0x0400),
        }

        # Create human-readable summary
        enabled_features = []
        if parsed_features["low_battery_detection"]:
            enabled_features.append("Low Battery Detection")
        if parsed_features["sensor_malfunction_detection"]:
            enabled_features.append("Sensor Malfunction Detection")
        if parsed_features["sensor_sample_size"]:
            enabled_features.append("Sensor Sample Size")
        if parsed_features["sensor_strip_insertion_error"]:
            enabled_features.append("Sensor Strip Insertion Error")
        if parsed_features["sensor_strip_type_error"]:
            enabled_features.append("Sensor Strip Type Error")
        if parsed_features["sensor_result_high_low"]:
            enabled_features.append("Sensor Result High-Low Detection")
        if parsed_features["sensor_temperature_high_low"]:
            enabled_features.append("Sensor Temperature High-Low Detection")
        if parsed_features["sensor_read_interrupt"]:
            enabled_features.append("Sensor Read Interrupt Detection")
        if parsed_features["general_device_fault"]:
            enabled_features.append("General Device Fault")
        if parsed_features["time_fault"]:
            enabled_features.append("Time Fault")
        if parsed_features["multiple_bond_support"]:
            enabled_features.append("Multiple Bond Support")

        parsed_features["enabled_features"] = enabled_features
        parsed_features["feature_count"] = len(enabled_features)

        return parsed_features

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

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return None  # Feature information, not a measurement

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return None  # Static feature information
