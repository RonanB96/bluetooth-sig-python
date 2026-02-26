"""Cross Trainer Data characteristic implementation.

Implements the Cross Trainer Data characteristic (0x2ACE) from the Fitness
Machine Service.  A 24-bit flags field (3 bytes) controls the presence of
optional data fields -- the widest flags field in the fitness machine set.

Bit 0 ("More Data") uses **inverted logic**: when bit 0 is 0 the
Instantaneous Speed field IS present; when bit 0 is 1 it is absent.
All other presence bits use normal logic (1 = present).

Bit 15 is a **semantic bit** (Movement Direction): 0 = Forward, 1 = Backward.
It does NOT gate any data fields.

References:
    Bluetooth SIG Fitness Machine Service 1.0
    org.bluetooth.characteristic.cross_trainer_data (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT8_MAX, UINT16_MAX, UINT24_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .fitness_machine_common import (
    MET_RESOLUTION,
    decode_elapsed_time,
    decode_energy_triplet,
    decode_heart_rate,
    decode_metabolic_equivalent,
    decode_remaining_time,
    encode_elapsed_time,
    encode_energy_triplet,
    encode_heart_rate,
    encode_metabolic_equivalent,
    encode_remaining_time,
)
from .utils import DataParser

# Speed: M=1, d=-2, b=0 -> actual = raw / 100 km/h
_SPEED_RESOLUTION = 100.0

# Stride Count: M=1, d=-1, b=0 -> actual = raw / 10
_STRIDE_COUNT_RESOLUTION = 10.0

# Inclination: M=1, d=-1, b=0 -> actual = raw / 10 %
# Ramp Setting: M=1, d=-1, b=0 -> actual = raw / 10 degrees
_TENTH_RESOLUTION = 10.0

# Resistance Level: M=1, d=1, b=0 -> actual = raw * 10
_RESISTANCE_RESOLUTION = 10.0


class CrossTrainerDataFlags(IntFlag):
    """Cross Trainer Data flags as per Bluetooth SIG specification.

    24-bit flags field (3 bytes).  Bit 0 uses inverted logic:
    0 = Instantaneous Speed present, 1 = absent.
    Bit 15 is a semantic modifier (Movement Direction), not a presence flag.
    """

    MORE_DATA = 0x000001  # Inverted: 0 -> Speed present, 1 -> absent
    AVERAGE_SPEED_PRESENT = 0x000002
    TOTAL_DISTANCE_PRESENT = 0x000004
    STEP_COUNT_PRESENT = 0x000008
    STRIDE_COUNT_PRESENT = 0x000010
    ELEVATION_GAIN_PRESENT = 0x000020
    INCLINATION_AND_RAMP_PRESENT = 0x000040
    RESISTANCE_LEVEL_PRESENT = 0x000080
    INSTANTANEOUS_POWER_PRESENT = 0x000100
    AVERAGE_POWER_PRESENT = 0x000200
    EXPENDED_ENERGY_PRESENT = 0x000400
    HEART_RATE_PRESENT = 0x000800
    METABOLIC_EQUIVALENT_PRESENT = 0x001000
    ELAPSED_TIME_PRESENT = 0x002000
    REMAINING_TIME_PRESENT = 0x004000
    MOVEMENT_DIRECTION_BACKWARD = 0x008000  # Semantic: 0=Forward, 1=Backward


class CrossTrainerData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Cross Trainer Data characteristic.

    Attributes:
        flags: Raw 24-bit flags field.
        instantaneous_speed: Instantaneous speed in km/h (0.01 resolution).
        average_speed: Average speed in km/h (0.01 resolution).
        total_distance: Total distance in metres (uint24).
        steps_per_minute: Steps per minute.
        average_step_rate: Average step rate in steps/min.
        stride_count: Stride count (0.1 resolution, a stride is a pair of steps).
        positive_elevation_gain: Positive elevation gain in metres.
        negative_elevation_gain: Negative elevation gain in metres.
        inclination: Current inclination in % (0.1 resolution, signed).
        ramp_setting: Current ramp angle in degrees (0.1 resolution, signed).
        resistance_level: Resistance level (unitless, resolution 10).
        instantaneous_power: Instantaneous power in watts (signed).
        average_power: Average power in watts (signed).
        total_energy: Total expended energy in kcal.
        energy_per_hour: Expended energy per hour in kcal.
        energy_per_minute: Expended energy per minute in kcal.
        heart_rate: Heart rate in bpm.
        metabolic_equivalent: MET value (0.1 resolution).
        elapsed_time: Elapsed time in seconds.
        remaining_time: Remaining time in seconds.
        movement_direction_backward: True if movement is backward, False if forward.

    """

    flags: CrossTrainerDataFlags
    instantaneous_speed: float | None = None
    average_speed: float | None = None
    total_distance: int | None = None
    steps_per_minute: int | None = None
    average_step_rate: int | None = None
    stride_count: float | None = None
    positive_elevation_gain: int | None = None
    negative_elevation_gain: int | None = None
    inclination: float | None = None
    ramp_setting: float | None = None
    resistance_level: float | None = None
    instantaneous_power: int | None = None
    average_power: int | None = None
    total_energy: int | None = None
    energy_per_hour: int | None = None
    energy_per_minute: int | None = None
    heart_rate: int | None = None
    metabolic_equivalent: float | None = None
    elapsed_time: int | None = None
    remaining_time: int | None = None
    movement_direction_backward: bool = False

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if (
            self.instantaneous_speed is not None
            and not 0.0 <= self.instantaneous_speed <= UINT16_MAX / _SPEED_RESOLUTION
        ):
            raise ValueError(
                f"Instantaneous speed must be 0.0-{UINT16_MAX / _SPEED_RESOLUTION}, got {self.instantaneous_speed}"
            )
        if self.average_speed is not None and not 0.0 <= self.average_speed <= UINT16_MAX / _SPEED_RESOLUTION:
            raise ValueError(f"Average speed must be 0.0-{UINT16_MAX / _SPEED_RESOLUTION}, got {self.average_speed}")
        if self.total_distance is not None and not 0 <= self.total_distance <= UINT24_MAX:
            raise ValueError(f"Total distance must be 0-{UINT24_MAX}, got {self.total_distance}")
        if self.steps_per_minute is not None and not 0 <= self.steps_per_minute <= UINT16_MAX:
            raise ValueError(f"Steps per minute must be 0-{UINT16_MAX}, got {self.steps_per_minute}")
        if self.average_step_rate is not None and not 0 <= self.average_step_rate <= UINT16_MAX:
            raise ValueError(f"Average step rate must be 0-{UINT16_MAX}, got {self.average_step_rate}")
        if self.stride_count is not None and not 0.0 <= self.stride_count <= UINT16_MAX / _STRIDE_COUNT_RESOLUTION:
            raise ValueError(
                f"Stride count must be 0.0-{UINT16_MAX / _STRIDE_COUNT_RESOLUTION}, got {self.stride_count}"
            )
        if self.positive_elevation_gain is not None and not 0 <= self.positive_elevation_gain <= UINT16_MAX:
            raise ValueError(f"Positive elevation must be 0-{UINT16_MAX}, got {self.positive_elevation_gain}")
        if self.negative_elevation_gain is not None and not 0 <= self.negative_elevation_gain <= UINT16_MAX:
            raise ValueError(f"Negative elevation must be 0-{UINT16_MAX}, got {self.negative_elevation_gain}")
        if (
            self.inclination is not None
            and not SINT16_MIN / _TENTH_RESOLUTION <= self.inclination <= SINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Inclination must be {SINT16_MIN / _TENTH_RESOLUTION}-{SINT16_MAX / _TENTH_RESOLUTION}, "
                f"got {self.inclination}"
            )
        if (
            self.ramp_setting is not None
            and not SINT16_MIN / _TENTH_RESOLUTION <= self.ramp_setting <= SINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Ramp setting must be {SINT16_MIN / _TENTH_RESOLUTION}-{SINT16_MAX / _TENTH_RESOLUTION}, "
                f"got {self.ramp_setting}"
            )
        if self.resistance_level is not None and not 0.0 <= self.resistance_level <= UINT8_MAX * _RESISTANCE_RESOLUTION:
            raise ValueError(
                f"Resistance level must be 0.0-{UINT8_MAX * _RESISTANCE_RESOLUTION}, got {self.resistance_level}"
            )
        if self.instantaneous_power is not None and not SINT16_MIN <= self.instantaneous_power <= SINT16_MAX:
            raise ValueError(f"Instantaneous power must be {SINT16_MIN}-{SINT16_MAX}, got {self.instantaneous_power}")
        if self.average_power is not None and not SINT16_MIN <= self.average_power <= SINT16_MAX:
            raise ValueError(f"Average power must be {SINT16_MIN}-{SINT16_MAX}, got {self.average_power}")
        if self.total_energy is not None and not 0 <= self.total_energy <= UINT16_MAX:
            raise ValueError(f"Total energy must be 0-{UINT16_MAX}, got {self.total_energy}")
        if self.energy_per_hour is not None and not 0 <= self.energy_per_hour <= UINT16_MAX:
            raise ValueError(f"Energy per hour must be 0-{UINT16_MAX}, got {self.energy_per_hour}")
        if self.energy_per_minute is not None and not 0 <= self.energy_per_minute <= UINT8_MAX:
            raise ValueError(f"Energy per minute must be 0-{UINT8_MAX}, got {self.energy_per_minute}")
        if self.heart_rate is not None and not 0 <= self.heart_rate <= UINT8_MAX:
            raise ValueError(f"Heart rate must be 0-{UINT8_MAX}, got {self.heart_rate}")
        if self.metabolic_equivalent is not None and not 0.0 <= self.metabolic_equivalent <= UINT8_MAX / MET_RESOLUTION:
            raise ValueError(
                f"Metabolic equivalent must be 0.0-{UINT8_MAX / MET_RESOLUTION}, got {self.metabolic_equivalent}"
            )
        if self.elapsed_time is not None and not 0 <= self.elapsed_time <= UINT16_MAX:
            raise ValueError(f"Elapsed time must be 0-{UINT16_MAX}, got {self.elapsed_time}")
        if self.remaining_time is not None and not 0 <= self.remaining_time <= UINT16_MAX:
            raise ValueError(f"Remaining time must be 0-{UINT16_MAX}, got {self.remaining_time}")


class CrossTrainerDataCharacteristic(BaseCharacteristic[CrossTrainerData]):
    """Cross Trainer Data characteristic (0x2ACE).

    Used in the Fitness Machine Service to transmit cross trainer workout
    data.  A 24-bit flags field (3 bytes) controls which optional fields
    are present -- the widest flags field in the fitness machine set.

    Flag-bit assignments (from GSS YAML):
        Bit 0: More Data -- **inverted**: 0 -> Inst. Speed present, 1 -> absent
        Bit 1: Average Speed present
        Bit 2: Total Distance present
        Bit 3: Step Count present (gates Steps/Min + Avg Step Rate)
        Bit 4: Stride Count present
        Bit 5: Elevation Gain present (gates Pos + Neg)
        Bit 6: Inclination and Ramp Angle Setting present (gates 2 fields)
        Bit 7: Resistance Level present
        Bit 8: Instantaneous Power present
        Bit 9: Average Power present
        Bit 10: Expended Energy present (gates triplet: total + /hr + /min)
        Bit 11: Heart Rate present
        Bit 12: Metabolic Equivalent present
        Bit 13: Elapsed Time present
        Bit 14: Remaining Time present
        Bit 15: Movement Direction (0=Forward, 1=Backward) -- semantic, not presence
        Bits 16-23: Reserved for Future Use

    """

    expected_type = CrossTrainerData
    min_length: int = 3  # Flags only (24-bit = 3 bytes)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CrossTrainerData:
        """Parse Cross Trainer Data from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CrossTrainerData with all present fields populated.

        """
        flags = CrossTrainerDataFlags(DataParser.parse_int24(data, 0, signed=False))
        offset = 3

        # Bit 0 -- inverted: Instantaneous Speed present when bit is NOT set
        instantaneous_speed = None
        if not (flags & CrossTrainerDataFlags.MORE_DATA) and len(data) >= offset + 2:
            raw_speed = DataParser.parse_int16(data, offset, signed=False)
            instantaneous_speed = raw_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 1 -- Average Speed
        average_speed = None
        if (flags & CrossTrainerDataFlags.AVERAGE_SPEED_PRESENT) and len(data) >= offset + 2:
            raw_avg_speed = DataParser.parse_int16(data, offset, signed=False)
            average_speed = raw_avg_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 2 -- Total Distance (uint24)
        total_distance = None
        if (flags & CrossTrainerDataFlags.TOTAL_DISTANCE_PRESENT) and len(data) >= offset + 3:
            total_distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        # Bit 3 -- Steps Per Minute (uint16) + Average Step Rate (uint16)
        steps_per_minute = None
        average_step_rate = None
        if (flags & CrossTrainerDataFlags.STEP_COUNT_PRESENT) and len(data) >= offset + 4:
            steps_per_minute = DataParser.parse_int16(data, offset, signed=False)
            offset += 2
            average_step_rate = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 4 -- Stride Count (uint16, d=-1 -> raw/10)
        stride_count = None
        if (flags & CrossTrainerDataFlags.STRIDE_COUNT_PRESENT) and len(data) >= offset + 2:
            raw_stride = DataParser.parse_int16(data, offset, signed=False)
            stride_count = raw_stride / _STRIDE_COUNT_RESOLUTION
            offset += 2

        # Bit 5 -- Positive Elevation Gain (uint16) + Negative Elevation Gain (uint16)
        positive_elevation_gain = None
        negative_elevation_gain = None
        if (flags & CrossTrainerDataFlags.ELEVATION_GAIN_PRESENT) and len(data) >= offset + 4:
            positive_elevation_gain = DataParser.parse_int16(data, offset, signed=False)
            offset += 2
            negative_elevation_gain = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 6 -- Inclination (sint16, d=-1) + Ramp Setting (sint16, d=-1)
        inclination = None
        ramp_setting = None
        if (flags & CrossTrainerDataFlags.INCLINATION_AND_RAMP_PRESENT) and len(data) >= offset + 4:
            raw_incl = DataParser.parse_int16(data, offset, signed=True)
            inclination = raw_incl / _TENTH_RESOLUTION
            offset += 2
            raw_ramp = DataParser.parse_int16(data, offset, signed=True)
            ramp_setting = raw_ramp / _TENTH_RESOLUTION
            offset += 2

        # Bit 7 -- Resistance Level (uint8, d=1 -> raw * 10)
        resistance_level = None
        if (flags & CrossTrainerDataFlags.RESISTANCE_LEVEL_PRESENT) and len(data) >= offset + 1:
            raw_resistance = DataParser.parse_int8(data, offset, signed=False)
            resistance_level = raw_resistance * _RESISTANCE_RESOLUTION
            offset += 1

        # Bit 8 -- Instantaneous Power (sint16)
        instantaneous_power = None
        if (flags & CrossTrainerDataFlags.INSTANTANEOUS_POWER_PRESENT) and len(data) >= offset + 2:
            instantaneous_power = DataParser.parse_int16(data, offset, signed=True)
            offset += 2

        # Bit 9 -- Average Power (sint16)
        average_power = None
        if (flags & CrossTrainerDataFlags.AVERAGE_POWER_PRESENT) and len(data) >= offset + 2:
            average_power = DataParser.parse_int16(data, offset, signed=True)
            offset += 2

        # Bit 10 -- Energy triplet (Total + Per Hour + Per Minute)
        total_energy = None
        energy_per_hour = None
        energy_per_minute = None
        if flags & CrossTrainerDataFlags.EXPENDED_ENERGY_PRESENT:
            total_energy, energy_per_hour, energy_per_minute, offset = decode_energy_triplet(data, offset)

        # Bit 11 -- Heart Rate
        heart_rate = None
        if flags & CrossTrainerDataFlags.HEART_RATE_PRESENT:
            heart_rate, offset = decode_heart_rate(data, offset)

        # Bit 12 -- Metabolic Equivalent
        metabolic_equivalent = None
        if flags & CrossTrainerDataFlags.METABOLIC_EQUIVALENT_PRESENT:
            metabolic_equivalent, offset = decode_metabolic_equivalent(data, offset)

        # Bit 13 -- Elapsed Time
        elapsed_time = None
        if flags & CrossTrainerDataFlags.ELAPSED_TIME_PRESENT:
            elapsed_time, offset = decode_elapsed_time(data, offset)

        # Bit 14 -- Remaining Time
        remaining_time = None
        if flags & CrossTrainerDataFlags.REMAINING_TIME_PRESENT:
            remaining_time, offset = decode_remaining_time(data, offset)

        # Bit 15 -- Movement Direction (semantic, no data fields)
        movement_direction_backward = bool(flags & CrossTrainerDataFlags.MOVEMENT_DIRECTION_BACKWARD)

        return CrossTrainerData(
            flags=flags,
            instantaneous_speed=instantaneous_speed,
            average_speed=average_speed,
            total_distance=total_distance,
            steps_per_minute=steps_per_minute,
            average_step_rate=average_step_rate,
            stride_count=stride_count,
            positive_elevation_gain=positive_elevation_gain,
            negative_elevation_gain=negative_elevation_gain,
            inclination=inclination,
            ramp_setting=ramp_setting,
            resistance_level=resistance_level,
            instantaneous_power=instantaneous_power,
            average_power=average_power,
            total_energy=total_energy,
            energy_per_hour=energy_per_hour,
            energy_per_minute=energy_per_minute,
            heart_rate=heart_rate,
            metabolic_equivalent=metabolic_equivalent,
            elapsed_time=elapsed_time,
            remaining_time=remaining_time,
            movement_direction_backward=movement_direction_backward,
        )

    def _encode_value(self, data: CrossTrainerData) -> bytearray:  # noqa: PLR0912
        """Encode CrossTrainerData back to BLE bytes.

        Reconstructs 24-bit flags from present fields so round-trip encoding
        preserves the original wire format.

        Args:
            data: CrossTrainerData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = CrossTrainerDataFlags(0)

        # Bit 0 -- inverted: set MORE_DATA when Speed is absent
        if data.instantaneous_speed is None:
            flags |= CrossTrainerDataFlags.MORE_DATA
        if data.average_speed is not None:
            flags |= CrossTrainerDataFlags.AVERAGE_SPEED_PRESENT
        if data.total_distance is not None:
            flags |= CrossTrainerDataFlags.TOTAL_DISTANCE_PRESENT
        if data.steps_per_minute is not None:
            flags |= CrossTrainerDataFlags.STEP_COUNT_PRESENT
        if data.stride_count is not None:
            flags |= CrossTrainerDataFlags.STRIDE_COUNT_PRESENT
        if data.positive_elevation_gain is not None:
            flags |= CrossTrainerDataFlags.ELEVATION_GAIN_PRESENT
        if data.inclination is not None:
            flags |= CrossTrainerDataFlags.INCLINATION_AND_RAMP_PRESENT
        if data.resistance_level is not None:
            flags |= CrossTrainerDataFlags.RESISTANCE_LEVEL_PRESENT
        if data.instantaneous_power is not None:
            flags |= CrossTrainerDataFlags.INSTANTANEOUS_POWER_PRESENT
        if data.average_power is not None:
            flags |= CrossTrainerDataFlags.AVERAGE_POWER_PRESENT
        if data.total_energy is not None:
            flags |= CrossTrainerDataFlags.EXPENDED_ENERGY_PRESENT
        if data.heart_rate is not None:
            flags |= CrossTrainerDataFlags.HEART_RATE_PRESENT
        if data.metabolic_equivalent is not None:
            flags |= CrossTrainerDataFlags.METABOLIC_EQUIVALENT_PRESENT
        if data.elapsed_time is not None:
            flags |= CrossTrainerDataFlags.ELAPSED_TIME_PRESENT
        if data.remaining_time is not None:
            flags |= CrossTrainerDataFlags.REMAINING_TIME_PRESENT
        if data.movement_direction_backward:
            flags |= CrossTrainerDataFlags.MOVEMENT_DIRECTION_BACKWARD

        result = DataParser.encode_int24(int(flags), signed=False)

        if data.instantaneous_speed is not None:
            raw_speed = round(data.instantaneous_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_speed, signed=False))
        if data.average_speed is not None:
            raw_avg_speed = round(data.average_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_avg_speed, signed=False))
        if data.total_distance is not None:
            result.extend(DataParser.encode_int24(data.total_distance, signed=False))
        if data.steps_per_minute is not None:
            result.extend(DataParser.encode_int16(data.steps_per_minute, signed=False))
        if data.average_step_rate is not None:
            result.extend(DataParser.encode_int16(data.average_step_rate, signed=False))
        if data.stride_count is not None:
            raw_stride = round(data.stride_count * _STRIDE_COUNT_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_stride, signed=False))
        if data.positive_elevation_gain is not None:
            result.extend(DataParser.encode_int16(data.positive_elevation_gain, signed=False))
        if data.negative_elevation_gain is not None:
            result.extend(DataParser.encode_int16(data.negative_elevation_gain, signed=False))
        if data.inclination is not None:
            raw_incl = round(data.inclination * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_incl, signed=True))
        if data.ramp_setting is not None:
            raw_ramp = round(data.ramp_setting * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_ramp, signed=True))
        if data.resistance_level is not None:
            raw_resistance = round(data.resistance_level / _RESISTANCE_RESOLUTION)
            result.extend(DataParser.encode_int8(raw_resistance, signed=False))
        if data.instantaneous_power is not None:
            result.extend(DataParser.encode_int16(data.instantaneous_power, signed=True))
        if data.average_power is not None:
            result.extend(DataParser.encode_int16(data.average_power, signed=True))
        if data.total_energy is not None:
            result.extend(encode_energy_triplet(data.total_energy, data.energy_per_hour, data.energy_per_minute))
        if data.heart_rate is not None:
            result.extend(encode_heart_rate(data.heart_rate))
        if data.metabolic_equivalent is not None:
            result.extend(encode_metabolic_equivalent(data.metabolic_equivalent))
        if data.elapsed_time is not None:
            result.extend(encode_elapsed_time(data.elapsed_time))
        if data.remaining_time is not None:
            result.extend(encode_remaining_time(data.remaining_time))

        return result
