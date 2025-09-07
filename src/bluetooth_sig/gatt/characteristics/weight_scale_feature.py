"""Weight Scale Feature characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass 
class WeightScaleFeatureData:
    """Parsed data from Weight Scale Feature characteristic."""
    
    raw_value: int
    timestamp_supported: bool
    multiple_users_supported: bool
    bmi_supported: bool
    weight_measurement_resolution: str
    height_measurement_resolution: str

    def __post_init__(self):
        """Validate weight scale feature data."""
        if not 0 <= self.raw_value <= 0xFFFFFFFF:
            raise ValueError("Raw value must be a 32-bit unsigned integer")


@dataclass
class WeightScaleFeatureCharacteristic(BaseCharacteristic):
    """Weight Scale Feature characteristic (0x2A9E).

    Used to indicate which optional features are supported by the weight scale.
    This is a read-only characteristic that describes device capabilities.
    """

    _characteristic_name: str = "Weight Scale Feature"

    def parse_value(self, data: bytearray) -> WeightScaleFeatureData:
        """Parse weight scale feature data according to Bluetooth specification.

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

        features_raw = struct.unpack("<L", data[:4])[0]

        # Parse feature flags according to specification
        return WeightScaleFeatureData(
            raw_value=features_raw,
            timestamp_supported=bool(features_raw & 0x01),
            multiple_users_supported=bool(features_raw & 0x02),
            bmi_supported=bool(features_raw & 0x04),
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
        if not isinstance(data, WeightScaleFeatureData):
            raise TypeError(
                f"Weight scale feature data must be a WeightScaleFeatureData, "
                f"got {type(data).__name__}"
            )

        # Use the raw value from the dataclass
        features_raw = data.raw_value
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
