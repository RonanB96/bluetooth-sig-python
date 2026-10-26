"""Cycling Power Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CyclingPowerFeatures(IntFlag):
    """Cycling Power Feature flags as per CPS v1.1 (bits 0-21)."""

    PEDAL_POWER_BALANCE_SUPPORTED = 0x00000001
    ACCUMULATED_TORQUE_SUPPORTED = 0x00000002
    WHEEL_REVOLUTION_DATA_SUPPORTED = 0x00000004
    CRANK_REVOLUTION_DATA_SUPPORTED = 0x00000008
    EXTREME_MAGNITUDES_SUPPORTED = 0x00000010
    EXTREME_ANGLES_SUPPORTED = 0x00000020
    TOP_AND_BOTTOM_DEAD_SPOT_ANGLES_SUPPORTED = 0x00000040
    ACCUMULATED_ENERGY_SUPPORTED = 0x00000080
    OFFSET_COMPENSATION_INDICATOR_SUPPORTED = 0x00000100
    OFFSET_COMPENSATION_SUPPORTED = 0x00000200
    CONTENT_MASKING_SUPPORTED = 0x00000400
    MULTIPLE_SENSOR_LOCATIONS_SUPPORTED = 0x00000800
    CRANK_LENGTH_ADJUSTMENT_SUPPORTED = 0x00001000
    CHAIN_LENGTH_ADJUSTMENT_SUPPORTED = 0x00002000
    CHAIN_WEIGHT_ADJUSTMENT_SUPPORTED = 0x00004000
    SPAN_LENGTH_ADJUSTMENT_SUPPORTED = 0x00008000
    SENSOR_MEASUREMENT_CONTEXT = 0x00010000
    INSTANTANEOUS_MEASUREMENT_DIRECTION_SUPPORTED = 0x00020000
    FACTORY_CALIBRATION_DATE_SUPPORTED = 0x00040000
    ENHANCED_OFFSET_COMPENSATION_SUPPORTED = 0x00080000
    DISTRIBUTED_SYSTEM_SUPPORT_BIT0 = 0x00100000
    DISTRIBUTED_SYSTEM_SUPPORT_BIT1 = 0x00200000


class CyclingPowerFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Cycling Power Feature characteristic."""

    features: CyclingPowerFeatures


class CyclingPowerFeatureCharacteristic(BaseCharacteristic[CyclingPowerFeatureData]):
    """Cycling Power Feature characteristic (0x2A65).

    Used to expose the supported features of a cycling power sensor.
    Contains a 32-bit bitmask indicating supported measurement
    capabilities (bits 0-21 per CPS v1.1).
    """

    expected_length: int = 4
    min_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CyclingPowerFeatureData:
        """Parse cycling power feature data.

        Format: 32-bit feature bitmask (little endian).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            CyclingPowerFeatureData containing parsed feature flags.

        Raises:
            ValueError: If data format is invalid.

        """
        feature_mask: int = DataParser.parse_int32(data, 0, signed=False)

        return CyclingPowerFeatureData(
            features=CyclingPowerFeatures(feature_mask),
        )

    def _encode_value(self, data: CyclingPowerFeatureData) -> bytearray:
        """Encode cycling power feature value back to bytes.

        Args:
            data: CyclingPowerFeatureData containing cycling power feature data

        Returns:
            Encoded bytes representing the cycling power features (uint32)

        """
        return DataParser.encode_int32(int(data.features), signed=False)
