"""Cycling Power Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CyclingPowerFeatures(IntFlag):
    """Cycling Power Feature flags as per Bluetooth SIG specification."""

    PEDAL_POWER_BALANCE_SUPPORTED = 0x01
    ACCUMULATED_ENERGY_SUPPORTED = 0x02
    WHEEL_REVOLUTION_DATA_SUPPORTED = 0x04
    CRANK_REVOLUTION_DATA_SUPPORTED = 0x08


class CyclingPowerFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Cycling Power Feature characteristic."""

    features: CyclingPowerFeatures
    pedal_power_balance_supported: bool
    accumulated_energy_supported: bool
    wheel_revolution_data_supported: bool
    crank_revolution_data_supported: bool


class CyclingPowerFeatureCharacteristic(BaseCharacteristic):
    """Cycling Power Feature characteristic (0x2A65).

    Used to expose the supported features of a cycling power sensor.
    Contains a 32-bit bitmask indicating supported measurement
    capabilities.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CyclingPowerFeatureData:
        """Parse cycling power feature data.

        Format: 32-bit feature bitmask (little endian).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            CyclingPowerFeatureData containing parsed feature flags.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 4:
            raise ValueError("Cycling Power Feature data must be at least 4 bytes")

        # Parse 32-bit unsigned integer (little endian)
        feature_mask: int = DataParser.parse_int32(data, 0, signed=False)

        # Parse feature flags according to specification
        return CyclingPowerFeatureData(
            features=CyclingPowerFeatures(feature_mask),
            pedal_power_balance_supported=bool(feature_mask & CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED),
            accumulated_energy_supported=bool(feature_mask & CyclingPowerFeatures.ACCUMULATED_ENERGY_SUPPORTED),
            wheel_revolution_data_supported=bool(feature_mask & CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED),
            crank_revolution_data_supported=bool(feature_mask & CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED),
        )

    def encode_value(self, data: CyclingPowerFeatureData) -> bytearray:
        """Encode cycling power feature value back to bytes.

        Args:
            data: CyclingPowerFeatureData containing cycling power feature data

        Returns:
            Encoded bytes representing the cycling power features (uint32)

        """
        # Reconstruct the features bitmap from individual flags
        features_bitmap = 0
        if data.pedal_power_balance_supported:
            features_bitmap |= CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
        if data.accumulated_energy_supported:
            features_bitmap |= CyclingPowerFeatures.ACCUMULATED_ENERGY_SUPPORTED
        if data.wheel_revolution_data_supported:
            features_bitmap |= CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
        if data.crank_revolution_data_supported:
            features_bitmap |= CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED

        return DataParser.encode_int32(features_bitmap, signed=False)
