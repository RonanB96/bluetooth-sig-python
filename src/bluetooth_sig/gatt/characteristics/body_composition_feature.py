"""Body Composition Feature characteristic implementation."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class BodyCompositionFeatureData:
    """Parsed data from Body Composition Feature characteristic."""
    
    raw_value: int
    timestamp_supported: bool
    multiple_users_supported: bool
    basal_metabolism_supported: bool
    muscle_mass_supported: bool
    muscle_percentage_supported: bool
    fat_free_mass_supported: bool
    soft_lean_mass_supported: bool
    body_water_mass_supported: bool
    impedance_supported: bool
    weight_supported: bool
    height_supported: bool
    mass_measurement_resolution: str
    height_measurement_resolution: str


@dataclass
class BodyCompositionFeatureCharacteristic(BaseCharacteristic):
    """Body Composition Feature characteristic (0x2A9B).

    Used to indicate which optional features and measurements are supported
    by the body composition device. This is a read-only characteristic that
    describes device capabilities.
    """

    _characteristic_name: str = "Body Composition Feature"

    def parse_value(self, data: bytearray) -> BodyCompositionFeatureData:
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
        return BodyCompositionFeatureData(
            raw_value=features_raw,
            # Basic features
            timestamp_supported=bool(features_raw & 0x01),
            multiple_users_supported=bool(features_raw & 0x02),
            basal_metabolism_supported=bool(features_raw & 0x04),
            muscle_mass_supported=bool(features_raw & 0x08),
            muscle_percentage_supported=bool(features_raw & 0x10),
            fat_free_mass_supported=bool(features_raw & 0x20),
            soft_lean_mass_supported=bool(features_raw & 0x40),
            body_water_mass_supported=bool(features_raw & 0x80),
            impedance_supported=bool(features_raw & 0x100),
            weight_supported=bool(features_raw & 0x200),
            height_supported=bool(features_raw & 0x400),
            # Mass measurement resolution (bits 11-14)
            mass_measurement_resolution=self._get_mass_resolution(features_raw),
            # Height measurement resolution (bits 15-17)
            height_measurement_resolution=self._get_height_resolution(features_raw),
        )

    def encode_value(self, data: BodyCompositionFeatureData) -> bytearray:
        """Encode BodyCompositionFeatureData back to bytes.
        
        Args:
            data: BodyCompositionFeatureData instance to encode
            
        Returns:
            Encoded bytes representing the body composition features
        """
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.timestamp_supported:
            features_bitmap |= 0x01
        if data.multiple_users_supported:
            features_bitmap |= 0x02
        if data.basal_metabolism_supported:
            features_bitmap |= 0x04
        if data.muscle_mass_supported:
            features_bitmap |= 0x08
        if data.muscle_percentage_supported:
            features_bitmap |= 0x10
        if data.fat_free_mass_supported:
            features_bitmap |= 0x20
        if data.soft_lean_mass_supported:
            features_bitmap |= 0x40
        if data.body_water_mass_supported:
            features_bitmap |= 0x80
        if data.impedance_supported:
            features_bitmap |= 0x100
        if data.weight_supported:
            features_bitmap |= 0x200
        if data.height_supported:
            features_bitmap |= 0x400
        
        # Note: For simplicity, we're not encoding the resolution fields back
        # since they require reverse mapping. The raw_value could be used instead
        # for full round-trip compatibility if needed.
            
        # Pack as little-endian 32-bit integer
        return bytearray(struct.pack("<L", features_bitmap))

    def _get_mass_resolution(self, features: int) -> str:
        """Extract mass measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            String describing mass resolution
        """
        resolution_bits = (features >> 11) & 0x0F  # Bits 11-14

        # Mass resolution lookup table
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
        resolution_bits = (features >> 15) & 0x07  # Bits 15-17

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
        return ""  # Feature characteristic has no unit
