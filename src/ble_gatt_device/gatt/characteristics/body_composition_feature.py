"""Body Composition Feature characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class BodyCompositionFeatureCharacteristic(BaseCharacteristic):
    """Body Composition Feature characteristic (0x2A9B).

    Used to indicate which optional features and measurements are supported by the body composition device.
    This is a read-only characteristic that describes device capabilities.
    """

    _characteristic_name: str = "Body Composition Feature"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"  # JSON string representation of features
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse body composition feature data according to Bluetooth specification.

        Format: Features(4 bytes) - bitmask indicating supported measurements

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed feature flags

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("Body Composition Feature data must be at least 4 bytes")

        features_raw = struct.unpack("<L", data[:4])[0]

        # Parse feature flags according to specification
        features = {
            "raw_value": features_raw,
            # Basic features
            "timestamp_supported": bool(features_raw & 0x01),
            "multiple_users_supported": bool(features_raw & 0x02),
            "basal_metabolism_supported": bool(features_raw & 0x04),
            "muscle_mass_supported": bool(features_raw & 0x08),
            "muscle_percentage_supported": bool(features_raw & 0x10),
            "fat_free_mass_supported": bool(features_raw & 0x20),
            "soft_lean_mass_supported": bool(features_raw & 0x40),
            "body_water_mass_supported": bool(features_raw & 0x80),
            "impedance_supported": bool(features_raw & 0x100),
            "weight_supported": bool(features_raw & 0x200),
            "height_supported": bool(features_raw & 0x400),
            
            # Mass measurement resolution (bits 11-14)
            "mass_measurement_resolution": self._get_mass_resolution(features_raw),
            
            # Height measurement resolution (bits 15-17)
            "height_measurement_resolution": self._get_height_resolution(features_raw),
        }

        return features

    def _get_mass_resolution(self, features: int) -> str:
        """Extract mass measurement resolution from features bitmask.
        
        Args:
            features: Raw feature bitmask
            
        Returns:
            String describing mass resolution
        """
        resolution_bits = (features >> 11) & 0x0F  # Bits 11-14
        
        if resolution_bits == 0:
            return "not_specified"
        elif resolution_bits == 1:
            return "0.5_kg_or_1_lb"
        elif resolution_bits == 2:
            return "0.2_kg_or_0.5_lb"
        elif resolution_bits == 3:
            return "0.1_kg_or_0.2_lb"
        elif resolution_bits == 4:
            return "0.05_kg_or_0.1_lb"
        elif resolution_bits == 5:
            return "0.02_kg_or_0.05_lb"
        elif resolution_bits == 6:
            return "0.01_kg_or_0.02_lb"
        elif resolution_bits == 7:
            return "0.005_kg_or_0.01_lb"
        else:
            return f"reserved_{resolution_bits}"

    def _get_height_resolution(self, features: int) -> str:
        """Extract height measurement resolution from features bitmask.
        
        Args:
            features: Raw feature bitmask
            
        Returns:
            String describing height resolution
        """
        resolution_bits = (features >> 15) & 0x07  # Bits 15-17
        
        if resolution_bits == 0:
            return "not_specified"
        elif resolution_bits == 1:
            return "0.01_m_or_1_inch"
        elif resolution_bits == 2:
            return "0.005_m_or_0.5_inch"
        elif resolution_bits == 3:
            return "0.001_m_or_0.1_inch"
        else:
            return f"reserved_{resolution_bits}"

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Feature characteristic has no unit

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return ""  # Feature characteristic is not a sensor

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Feature characteristic is not measured