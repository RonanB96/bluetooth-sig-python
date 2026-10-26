"""Fitness Machine Feature characteristic (0x2ACC)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class FitnessMachineFeatures(IntFlag):
    """Fitness Machine feature flags (bits 0-16 of first uint32)."""

    AVERAGE_SPEED_SUPPORTED = 0x0001
    CADENCE_SUPPORTED = 0x0002
    TOTAL_DISTANCE_SUPPORTED = 0x0004
    INCLINATION_SUPPORTED = 0x0008
    ELEVATION_GAIN_SUPPORTED = 0x0010
    PACE_SUPPORTED = 0x0020
    STEP_COUNT_SUPPORTED = 0x0040
    RESISTANCE_LEVEL_SUPPORTED = 0x0080
    STAIR_COUNT_SUPPORTED = 0x0100
    EXPENDED_ENERGY_SUPPORTED = 0x0200
    HEART_RATE_MEASUREMENT_SUPPORTED = 0x0400
    METABOLIC_EQUIVALENT_SUPPORTED = 0x0800
    ELAPSED_TIME_SUPPORTED = 0x1000
    REMAINING_TIME_SUPPORTED = 0x2000
    POWER_MEASUREMENT_SUPPORTED = 0x4000
    FORCE_ON_BELT_AND_POWER_OUTPUT_SUPPORTED = 0x8000
    USER_DATA_RETENTION_SUPPORTED = 0x10000


class TargetSettingFeatures(IntFlag):
    """Target Setting feature flags (bits 0-13 of second uint32)."""

    SPEED_TARGET_SETTING_SUPPORTED = 0x0001
    INCLINATION_TARGET_SETTING_SUPPORTED = 0x0002
    RESISTANCE_TARGET_SETTING_SUPPORTED = 0x0004
    POWER_TARGET_SETTING_SUPPORTED = 0x0008
    HEART_RATE_TARGET_SETTING_SUPPORTED = 0x0010
    TARGETED_EXPENDED_ENERGY_CONFIGURATION_SUPPORTED = 0x0020
    TARGETED_STEP_NUMBER_CONFIGURATION_SUPPORTED = 0x0040
    TARGETED_STRIDE_NUMBER_CONFIGURATION_SUPPORTED = 0x0080
    TARGETED_DISTANCE_CONFIGURATION_SUPPORTED = 0x0100
    TARGETED_TRAINING_TIME_CONFIGURATION_SUPPORTED = 0x0200
    TARGETED_TIME_IN_TWO_HEART_RATE_ZONES_CONFIGURATION_SUPPORTED = 0x0400
    TARGETED_TIME_IN_THREE_HEART_RATE_ZONES_CONFIGURATION_SUPPORTED = 0x0800
    TARGETED_TIME_IN_FIVE_HEART_RATE_ZONES_CONFIGURATION_SUPPORTED = 0x1000
    INDOOR_BIKE_SIMULATION_PARAMETERS_SUPPORTED = 0x2000


class FitnessMachineFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for Fitness Machine Feature characteristic.

    Contains two bitfields: machine features and target setting features.
    """

    fitness_machine_features: FitnessMachineFeatures
    target_setting_features: TargetSettingFeatures


class FitnessMachineFeatureCharacteristic(BaseCharacteristic[FitnessMachineFeatureData]):
    """Fitness Machine Feature characteristic (0x2ACC).

    org.bluetooth.characteristic.fitness_machine_feature

    Describes the supported features of the fitness machine and
    the supported target settings.
    """

    expected_length: int = 8  # 2 x uint32
    min_length: int = 8
    expected_type = FitnessMachineFeatureData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> FitnessMachineFeatureData:
        """Parse Fitness Machine Feature data (2 x uint32 bitfields).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            FitnessMachineFeatureData with machine and target setting features.

        """
        machine_raw = DataParser.parse_int32(data, 0, signed=False)
        target_raw = DataParser.parse_int32(data, 4, signed=False)

        return FitnessMachineFeatureData(
            fitness_machine_features=FitnessMachineFeatures(machine_raw),
            target_setting_features=TargetSettingFeatures(target_raw),
        )

    def _encode_value(self, data: FitnessMachineFeatureData) -> bytearray:
        """Encode Fitness Machine Feature data to bytes.

        Args:
            data: FitnessMachineFeatureData instance.

        Returns:
            Encoded bytes (2 x uint32, little-endian).

        """
        if not isinstance(data, FitnessMachineFeatureData):
            raise TypeError(f"Expected FitnessMachineFeatureData, got {type(data).__name__}")

        result = bytearray()
        result.extend(DataParser.encode_int32(int(data.fitness_machine_features), signed=False))
        result.extend(DataParser.encode_int32(int(data.target_setting_features), signed=False))
        return result
