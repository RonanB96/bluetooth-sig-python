"""Physical Activity Monitor Features characteristic (0x2B3B).

64-bit bitfield of supported Physical Activity Monitor features.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class PhysicalActivityMonitorFeatures(IntFlag):
    """Physical Activity Monitor feature flags (uint64, 8 octets)."""

    MULTIPLE_USERS_SUPPORTED = 1 << 0
    USER_DATA_SERVICE_SUPPORTED = 1 << 1
    DEVICE_WORN_SUPPORTED = 1 << 2
    NORMAL_WALKING_ENERGY_EXPENDITURE_SUPPORTED = 1 << 3
    NORMAL_WALKING_ENERGY_EXPENDITURE_PER_HOUR_SUPPORTED = 1 << 4
    INTENSITY_ENERGY_EXPENDITURE_SUPPORTED = 1 << 5
    INTENSITY_ENERGY_EXPENDITURE_PER_HOUR_SUPPORTED = 1 << 6
    TOTAL_ENERGY_EXPENDITURE_SUPPORTED = 1 << 7
    TOTAL_ENERGY_EXPENDITURE_PER_HOUR_SUPPORTED = 1 << 8
    FAT_BURNED_SUPPORTED = 1 << 9
    FAT_BURNED_PER_HOUR_SUPPORTED = 1 << 10
    METABOLIC_EQUIVALENT_SUPPORTED = 1 << 11
    DISTANCE_SUPPORTED = 1 << 12
    SPEED_SUPPORTED = 1 << 13
    DURATION_NORMAL_WALKING_EPISODES_SUPPORTED = 1 << 14
    DURATION_INTENSITY_WALKING_EPISODES_SUPPORTED = 1 << 15
    MOTION_CADENCE_SUPPORTED = 1 << 16
    FLOORS_SUPPORTED = 1 << 17
    POSITIVE_ELEVATION_GAIN_SUPPORTED = 1 << 18
    NEGATIVE_ELEVATION_GAIN_SUPPORTED = 1 << 19
    ELEVATION_SUPPORTED = 1 << 20
    ACTIVITY_COUNT_SUPPORTED = 1 << 21
    ACTIVITY_COUNT_PER_MINUTE_SUPPORTED = 1 << 22
    ACTIVITY_LEVEL_SUPPORTED = 1 << 23
    ACTIVITY_TYPE_SUPPORTED = 1 << 24
    WORN_DURATION_SUPPORTED = 1 << 25
    TIME_IN_HR_ZONE1_SUPPORTED = 1 << 26
    TIME_IN_HR_ZONE2_SUPPORTED = 1 << 27
    TIME_IN_HR_ZONE3_SUPPORTED = 1 << 28
    TIME_IN_HR_ZONE4_SUPPORTED = 1 << 29
    TIME_IN_HR_ZONE5_SUPPORTED = 1 << 30
    VO2_MAX_SUPPORTED = 1 << 31
    HEART_RATE_SUPPORTED = 1 << 32
    PULSE_INTER_BEAT_INTERVAL_SUPPORTED = 1 << 33
    RESTING_HEART_RATE_SUPPORTED = 1 << 34
    HEART_RATE_VARIABILITY_SUPPORTED = 1 << 35
    RESPIRATION_RATE_SUPPORTED = 1 << 36
    RESTING_RESPIRATION_RATE_SUPPORTED = 1 << 37
    NORMAL_WALKING_STEPS_SUPPORTED = 1 << 38
    INTENSITY_STEPS_SUPPORTED = 1 << 39
    FLOOR_STEPS_SUPPORTED = 1 << 40
    TOTAL_SLEEP_TIME_SUPPORTED = 1 << 41
    TOTAL_WAKE_TIME_SUPPORTED = 1 << 42
    TOTAL_BED_TIME_SUPPORTED = 1 << 43
    NUMBER_OF_AWAKENINGS_SUPPORTED = 1 << 44
    SLEEP_LATENCY_SUPPORTED = 1 << 45
    SLEEP_EFFICIENCY_SUPPORTED = 1 << 46
    SNOOZE_TIME_SUPPORTED = 1 << 47
    NUMBER_OF_TOSS_AND_TURN_EVENTS_SUPPORTED = 1 << 48
    TIME_OF_AWAKENING_AFTER_ALARM_SUPPORTED = 1 << 49
    VISIBLE_LIGHT_LEVEL_SUPPORTED = 1 << 50
    UV_LIGHT_LEVEL_SUPPORTED = 1 << 51
    IR_LIGHT_LEVEL_SUPPORTED = 1 << 52
    SLEEP_STAGE_SUPPORTED = 1 << 53
    SLEEPING_HEART_RATE_SUPPORTED = 1 << 54


class PhysicalActivityMonitorFeaturesCharacteristic(BaseCharacteristic[PhysicalActivityMonitorFeatures]):
    """Physical Activity Monitor Features characteristic (0x2B3B).

    org.bluetooth.characteristic.physical_activity_monitor_features

    Reports supported features of the Physical Activity Monitor.
    64-bit feature bitfield (8 octets, no FlagTemplate.uint64 available).
    """

    min_length = 8
    allow_variable_length = False

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PhysicalActivityMonitorFeatures:
        """Parse Physical Activity Monitor Features (uint64 LE)."""
        raw = int.from_bytes(data[:8], byteorder="little")
        return PhysicalActivityMonitorFeatures(raw)

    def _encode_value(self, data: PhysicalActivityMonitorFeatures) -> bytearray:
        """Encode Physical Activity Monitor Features (uint64 LE)."""
        return bytearray(int(data).to_bytes(8, byteorder="little"))
