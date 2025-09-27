"""Body Composition Feature characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

from .base import BaseCharacteristic
from .utils import BitFieldUtils, DataParser


class BodyCompositionFeatureBits:
    """Body Composition Feature bit field constants."""

    # pylint: disable=too-few-public-methods

    MASS_RESOLUTION_START_BIT = 11  # Mass resolution starts at bit 11
    MASS_RESOLUTION_BIT_WIDTH = 4  # Mass resolution uses 4 bits
    HEIGHT_RESOLUTION_START_BIT = 15  # Height resolution starts at bit 15
    HEIGHT_RESOLUTION_BIT_WIDTH = 3  # Height resolution uses 3 bits


class MassMeasurementResolution(IntEnum):
    """Mass measurement resolution enumeration."""

    NOT_SPECIFIED = 0
    KG_0_5_OR_LB_1 = 1
    KG_0_2_OR_LB_0_5 = 2
    KG_0_1_OR_LB_0_2 = 3
    KG_0_05_OR_LB_0_1 = 4
    KG_0_02_OR_LB_0_05 = 5
    KG_0_01_OR_LB_0_02 = 6
    KG_0_005_OR_LB_0_01 = 7

    def __str__(self) -> str:
        """Return human-readable mass resolution description."""
        descriptions = {
            self.NOT_SPECIFIED: "not_specified",
            self.KG_0_5_OR_LB_1: "0.5_kg_or_1_lb",
            self.KG_0_2_OR_LB_0_5: "0.2_kg_or_0.5_lb",
            self.KG_0_1_OR_LB_0_2: "0.1_kg_or_0.2_lb",
            self.KG_0_05_OR_LB_0_1: "0.05_kg_or_0.1_lb",
            self.KG_0_02_OR_LB_0_05: "0.02_kg_or_0.05_lb",
            self.KG_0_01_OR_LB_0_02: "0.01_kg_or_0.02_lb",
            self.KG_0_005_OR_LB_0_01: "0.005_kg_or_0.01_lb",
        }
        return descriptions.get(self, "Reserved for Future Use")


class HeightMeasurementResolution(IntEnum):
    """Height measurement resolution enumeration."""

    NOT_SPECIFIED = 0
    M_0_01_OR_INCH_1 = 1
    M_0_005_OR_INCH_0_5 = 2
    M_0_001_OR_INCH_0_1 = 3

    def __str__(self) -> str:
        """Return human-readable height resolution description."""
        descriptions = {
            self.NOT_SPECIFIED: "not_specified",
            self.M_0_01_OR_INCH_1: "0.01_m_or_1_inch",
            self.M_0_005_OR_INCH_0_5: "0.005_m_or_0.5_inch",
            self.M_0_001_OR_INCH_0_1: "0.001_m_or_0.1_inch",
        }
        return descriptions.get(self, "Reserved for Future Use")


class BodyCompositionFeatures(IntFlag):
    """Body Composition Feature flags as per Bluetooth SIG specification."""

    TIMESTAMP_SUPPORTED = 0x01
    MULTIPLE_USERS_SUPPORTED = 0x02
    BASAL_METABOLISM_SUPPORTED = 0x04
    MUSCLE_MASS_SUPPORTED = 0x08
    MUSCLE_PERCENTAGE_SUPPORTED = 0x10
    FAT_FREE_MASS_SUPPORTED = 0x20
    SOFT_LEAN_MASS_SUPPORTED = 0x40
    BODY_WATER_MASS_SUPPORTED = 0x80
    IMPEDANCE_SUPPORTED = 0x100
    WEIGHT_SUPPORTED = 0x200
    HEIGHT_SUPPORTED = 0x400


@dataclass
class BodyCompositionFeatureData:  # pylint: disable=too-many-instance-attributes
    """Parsed data from Body Composition Feature characteristic."""

    features: BodyCompositionFeatures
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
    mass_measurement_resolution: MassMeasurementResolution
    height_measurement_resolution: HeightMeasurementResolution


@dataclass
class BodyCompositionFeatureCharacteristic(BaseCharacteristic):
    """Body Composition Feature characteristic (0x2A9B).

    Used to indicate which optional features and measurements are supported
    by the body composition device. This is a read-only characteristic that
    describes device capabilities.
    """

    _characteristic_name: str = "Body Composition Feature"

    min_length: int = 4  # Features(4) fixed length
    max_length: int = 4  # Features(4) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(
        self, data: bytearray, ctx: Any | None = None
    ) -> BodyCompositionFeatureData:
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

        features_raw = DataParser.parse_int32(data, 0, signed=False)

        # Parse feature flags according to specification
        return BodyCompositionFeatureData(
            features=BodyCompositionFeatures(features_raw),
            # Basic features
            timestamp_supported=bool(
                features_raw & BodyCompositionFeatures.TIMESTAMP_SUPPORTED
            ),
            multiple_users_supported=bool(
                features_raw & BodyCompositionFeatures.MULTIPLE_USERS_SUPPORTED
            ),
            basal_metabolism_supported=bool(
                features_raw & BodyCompositionFeatures.BASAL_METABOLISM_SUPPORTED
            ),
            muscle_mass_supported=bool(
                features_raw & BodyCompositionFeatures.MUSCLE_MASS_SUPPORTED
            ),
            muscle_percentage_supported=bool(
                features_raw & BodyCompositionFeatures.MUSCLE_PERCENTAGE_SUPPORTED
            ),
            fat_free_mass_supported=bool(
                features_raw & BodyCompositionFeatures.FAT_FREE_MASS_SUPPORTED
            ),
            soft_lean_mass_supported=bool(
                features_raw & BodyCompositionFeatures.SOFT_LEAN_MASS_SUPPORTED
            ),
            body_water_mass_supported=bool(
                features_raw & BodyCompositionFeatures.BODY_WATER_MASS_SUPPORTED
            ),
            impedance_supported=bool(
                features_raw & BodyCompositionFeatures.IMPEDANCE_SUPPORTED
            ),
            weight_supported=bool(
                features_raw & BodyCompositionFeatures.WEIGHT_SUPPORTED
            ),
            height_supported=bool(
                features_raw & BodyCompositionFeatures.HEIGHT_SUPPORTED
            ),
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
            features_bitmap |= BodyCompositionFeatures.TIMESTAMP_SUPPORTED
        if data.multiple_users_supported:
            features_bitmap |= BodyCompositionFeatures.MULTIPLE_USERS_SUPPORTED
        if data.basal_metabolism_supported:
            features_bitmap |= BodyCompositionFeatures.BASAL_METABOLISM_SUPPORTED
        if data.muscle_mass_supported:
            features_bitmap |= BodyCompositionFeatures.MUSCLE_MASS_SUPPORTED
        if data.muscle_percentage_supported:
            features_bitmap |= BodyCompositionFeatures.MUSCLE_PERCENTAGE_SUPPORTED
        if data.fat_free_mass_supported:
            features_bitmap |= BodyCompositionFeatures.FAT_FREE_MASS_SUPPORTED
        if data.soft_lean_mass_supported:
            features_bitmap |= BodyCompositionFeatures.SOFT_LEAN_MASS_SUPPORTED
        if data.body_water_mass_supported:
            features_bitmap |= BodyCompositionFeatures.BODY_WATER_MASS_SUPPORTED
        if data.impedance_supported:
            features_bitmap |= BodyCompositionFeatures.IMPEDANCE_SUPPORTED
        if data.weight_supported:
            features_bitmap |= BodyCompositionFeatures.WEIGHT_SUPPORTED
        if data.height_supported:
            features_bitmap |= BodyCompositionFeatures.HEIGHT_SUPPORTED

        # Note: For simplicity, we're not encoding the resolution fields back
        # since they require reverse mapping. The raw_value could be used instead
        # for full round-trip compatibility if needed.

        # Pack as little-endian 32-bit integer
        return bytearray(DataParser.encode_int32(features_bitmap, signed=False))

    def _get_mass_resolution(self, features: int) -> MassMeasurementResolution:
        """Extract mass measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            MassMeasurementResolution enum value
        """
        resolution_bits = BitFieldUtils.extract_bit_field(
            features,
            BodyCompositionFeatureBits.MASS_RESOLUTION_START_BIT,
            BodyCompositionFeatureBits.MASS_RESOLUTION_BIT_WIDTH,
        )  # Bits 11-14 (4 bits)

        try:
            return MassMeasurementResolution(resolution_bits)
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return MassMeasurementResolution.NOT_SPECIFIED

    def _get_height_resolution(self, features: int) -> HeightMeasurementResolution:
        """Extract height measurement resolution from features bitmask.

        Args:
            features: Raw feature bitmask

        Returns:
            HeightMeasurementResolution enum value
        """
        resolution_bits = BitFieldUtils.extract_bit_field(
            features,
            BodyCompositionFeatureBits.HEIGHT_RESOLUTION_START_BIT,
            BodyCompositionFeatureBits.HEIGHT_RESOLUTION_BIT_WIDTH,
        )  # Bits 15-17 (3 bits)

        try:
            return HeightMeasurementResolution(resolution_bits)
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return HeightMeasurementResolution.NOT_SPECIFIED

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Feature characteristic has no unit
