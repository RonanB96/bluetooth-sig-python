"""Weight Scale Feature characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class WeightScaleFeatureCharacteristic(BaseCharacteristic):
    """Weight Scale Feature characteristic (0x2A9E).

    Used to indicate which optional features are supported by the weight scale.
    This is a read-only characteristic that describes device capabilities.
    """

    _characteristic_name: str = "Weight Scale Feature"

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse weight scale feature data according to Bluetooth specification.

        Format: Features(4 bytes) - bitmask indicating supported features

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed feature flags

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("Weight Scale Feature data must be at least 4 bytes")

        features_raw = struct.unpack("<L", data[:4])[0]

        # Parse feature flags according to specification
        features = {
            "raw_value": features_raw,
            "timestamp_supported": bool(features_raw & 0x01),
            "multiple_users_supported": bool(features_raw & 0x02),
            "bmi_supported": bool(features_raw & 0x04),
            "weight_measurement_resolution": self._get_weight_resolution(features_raw),
            "height_measurement_resolution": self._get_height_resolution(features_raw),
        }

        return features

    def encode_value(self, data: dict[str, Any] | int) -> bytearray:
        """Encode weight scale feature value back to bytes.

        Args:
            data: Dictionary with feature flags or raw integer value

        Returns:
            Encoded bytes representing the weight scale features (uint32)
        """
        if isinstance(data, int):
            # Direct raw value
            features_raw = data
        elif isinstance(data, dict):
            # Build from feature flags
            features_raw = data.get("raw_value", 0)

            # If raw_value not provided, build from individual flags
            if features_raw == 0:
                if data.get("timestamp_supported", False):
                    features_raw |= 0x01
                if data.get("multiple_users_supported", False):
                    features_raw |= 0x02
                if data.get("bmi_supported", False):
                    features_raw |= 0x04

                # Add weight resolution bits (bits 3-6)
                weight_res = data.get("weight_measurement_resolution", "not_specified")
                weight_res_map = {
                    "not_specified": 0,
                    "0.5_kg_or_1_lb": 1,
                    "0.2_kg_or_0.5_lb": 2,
                    "0.1_kg_or_0.2_lb": 3,
                    "0.05_kg_or_0.1_lb": 4,
                    "0.02_kg_or_0.05_lb": 5,
                    "0.01_kg_or_0.02_lb": 6,
                    "0.005_kg_or_0.01_lb": 7,
                }
                if weight_res in weight_res_map:
                    features_raw |= weight_res_map[weight_res] << 3

                # Add height resolution bits (bits 7-9)
                height_res = data.get("height_measurement_resolution", "not_specified")
                height_res_map = {
                    "not_specified": 0,
                    "0.01_m_or_1_inch": 1,
                    "0.005_m_or_0.5_inch": 2,
                    "0.001_m_or_0.1_inch": 3,
                }
                if height_res in height_res_map:
                    features_raw |= height_res_map[height_res] << 7
        else:
            raise TypeError("Weight scale feature data must be a dictionary or integer")

        # Validate range for uint32
        if not 0 <= features_raw <= 0xFFFFFFFF:
            raise ValueError(f"Features value {features_raw} exceeds uint32 range")

        return bytearray(struct.pack("<I", features_raw))

    def _get_weight_resolution(self, features: int) -> str:
        """Extract weight measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            String describing weight resolution
        """
        resolution_bits = (features >> 3) & 0x0F  # Bits 3-6

        # Weight resolution lookup table
        resolution_map = {
            0: "not_specified",
            1: "0.5_kg_or_1_lb",
            2: "0.2_kg_or_0.5_lb",
            3: "0.1_kg_or_0.2_lb",
            4: "0.05_kg_or_0.1_lb",
            5: "0.02_kg_or_0.05_lb",
            6: "0.01_kg_or_0.02_lb",
            7: "0.005_kg_or_0.01_lb",
        }

        return resolution_map.get(resolution_bits, f"reserved_{resolution_bits}")

    def _get_height_resolution(self, features: int) -> str:
        """Extract height measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            String describing height resolution
        """
        resolution_bits = (features >> 7) & 0x07  # Bits 7-9

        # Height resolution lookup table
        resolution_map = {
            0: "not_specified",
            1: "0.01_m_or_1_inch",
            2: "0.005_m_or_0.5_inch",
            3: "0.001_m_or_0.1_inch",
        }

        return resolution_map.get(resolution_bits, f"reserved_{resolution_bits}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Feature characteristic has no unit        return ""  # Feature characteristic is not measured
