"""Treadmill Data characteristic implementation.

Implements the Treadmill Data characteristic (0x2ACD) from the Fitness Machine
Service.  A 16-bit flags field controls the presence of optional data fields.

Bit 0 ("More Data") uses **inverted logic**: when bit 0 is 0 the
Instantaneous Speed field IS present; when bit 0 is 1 it is absent.
All other bits use normal logic (1 = present).

References:
    Bluetooth SIG Fitness Machine Service 1.0
    org.bluetooth.characteristic.treadmill_data (GSS YAML)
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

# Inclination: M=1, d=-1, b=0 -> actual = raw / 10 %
# Ramp Angle: M=1, d=-1, b=0 -> actual = raw / 10 degrees
# Elevation: M=1, d=-1, b=0 -> actual = raw / 10 metres
_TENTH_RESOLUTION = 10.0


class TreadmillDataFlags(IntFlag):
    """Treadmill Data flags as per Bluetooth SIG specification.

    Bit 0 uses inverted logic: 0 = Instantaneous Speed present, 1 = absent.
    """

    MORE_DATA = 0x0001  # Inverted: 0 -> Speed present, 1 -> absent
    AVERAGE_SPEED_PRESENT = 0x0002
    TOTAL_DISTANCE_PRESENT = 0x0004
    INCLINATION_AND_RAMP_PRESENT = 0x0008
    ELEVATION_GAIN_PRESENT = 0x0010
    INSTANTANEOUS_PACE_PRESENT = 0x0020
    AVERAGE_PACE_PRESENT = 0x0040
    EXPENDED_ENERGY_PRESENT = 0x0080
    HEART_RATE_PRESENT = 0x0100
    METABOLIC_EQUIVALENT_PRESENT = 0x0200
    ELAPSED_TIME_PRESENT = 0x0400
    REMAINING_TIME_PRESENT = 0x0800
    FORCE_AND_POWER_PRESENT = 0x1000


class TreadmillData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Treadmill Data characteristic.

    Attributes:
        flags: Raw 16-bit flags field.
        instantaneous_speed: Instantaneous belt speed in km/h (0.01 resolution).
        average_speed: Average speed in km/h (0.01 resolution).
        total_distance: Total distance in metres (uint24).
        inclination: Current inclination in % (0.1 resolution, signed).
        ramp_angle_setting: Current ramp angle in degrees (0.1 resolution, signed).
        positive_elevation_gain: Positive elevation gain in metres (0.1 resolution).
        negative_elevation_gain: Negative elevation gain in metres (0.1 resolution).
        instantaneous_pace: Instantaneous pace in seconds per 500 m.
        average_pace: Average pace in seconds per 500 m.
        total_energy: Total expended energy in kcal.
        energy_per_hour: Expended energy per hour in kcal.
        energy_per_minute: Expended energy per minute in kcal.
        heart_rate: Heart rate in bpm.
        metabolic_equivalent: MET value (0.1 resolution).
        elapsed_time: Elapsed time in seconds.
        remaining_time: Remaining time in seconds.
        force_on_belt: Force on belt in newtons (signed).
        power_output: Power output in watts (signed).

    """

    flags: TreadmillDataFlags
    instantaneous_speed: float | None = None
    average_speed: float | None = None
    total_distance: int | None = None
    inclination: float | None = None
    ramp_angle_setting: float | None = None
    positive_elevation_gain: float | None = None
    negative_elevation_gain: float | None = None
    instantaneous_pace: int | None = None
    average_pace: int | None = None
    total_energy: int | None = None
    energy_per_hour: int | None = None
    energy_per_minute: int | None = None
    heart_rate: int | None = None
    metabolic_equivalent: float | None = None
    elapsed_time: int | None = None
    remaining_time: int | None = None
    force_on_belt: int | None = None
    power_output: int | None = None

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
        if (
            self.inclination is not None
            and not SINT16_MIN / _TENTH_RESOLUTION <= self.inclination <= SINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Inclination must be {SINT16_MIN / _TENTH_RESOLUTION}-{SINT16_MAX / _TENTH_RESOLUTION}, "
                f"got {self.inclination}"
            )
        if (
            self.ramp_angle_setting is not None
            and not SINT16_MIN / _TENTH_RESOLUTION <= self.ramp_angle_setting <= SINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Ramp angle must be {SINT16_MIN / _TENTH_RESOLUTION}-{SINT16_MAX / _TENTH_RESOLUTION}, "
                f"got {self.ramp_angle_setting}"
            )
        if (
            self.positive_elevation_gain is not None
            and not 0.0 <= self.positive_elevation_gain <= UINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Positive elevation must be 0.0-{UINT16_MAX / _TENTH_RESOLUTION}, got {self.positive_elevation_gain}"
            )
        if (
            self.negative_elevation_gain is not None
            and not 0.0 <= self.negative_elevation_gain <= UINT16_MAX / _TENTH_RESOLUTION
        ):
            raise ValueError(
                f"Negative elevation must be 0.0-{UINT16_MAX / _TENTH_RESOLUTION}, got {self.negative_elevation_gain}"
            )
        if self.instantaneous_pace is not None and not 0 <= self.instantaneous_pace <= UINT16_MAX:
            raise ValueError(f"Instantaneous pace must be 0-{UINT16_MAX}, got {self.instantaneous_pace}")
        if self.average_pace is not None and not 0 <= self.average_pace <= UINT16_MAX:
            raise ValueError(f"Average pace must be 0-{UINT16_MAX}, got {self.average_pace}")
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
        if self.force_on_belt is not None and not SINT16_MIN <= self.force_on_belt <= SINT16_MAX:
            raise ValueError(f"Force on belt must be {SINT16_MIN}-{SINT16_MAX}, got {self.force_on_belt}")
        if self.power_output is not None and not SINT16_MIN <= self.power_output <= SINT16_MAX:
            raise ValueError(f"Power output must be {SINT16_MIN}-{SINT16_MAX}, got {self.power_output}")


class TreadmillDataCharacteristic(BaseCharacteristic[TreadmillData]):
    """Treadmill Data characteristic (0x2ACD).

    Used in the Fitness Machine Service to transmit treadmill workout data.
    A 16-bit flags field controls which optional fields are present.

    Flag-bit assignments (from GSS YAML):
        Bit 0: More Data -- **inverted**: 0 -> Inst. Speed present, 1 -> absent
        Bit 1: Average Speed present
        Bit 2: Total Distance present
        Bit 3: Inclination and Ramp Angle Setting present (gates 2 fields)
        Bit 4: Elevation Gain present (gates 2 fields: pos + neg)
        Bit 5: Instantaneous Pace present
        Bit 6: Average Pace present
        Bit 7: Expended Energy present (gates triplet: total + /hr + /min)
        Bit 8: Heart Rate present
        Bit 9: Metabolic Equivalent present
        Bit 10: Elapsed Time present
        Bit 11: Remaining Time present
        Bit 12: Force On Belt and Power Output present (gates 2 fields)
        Bits 13-15: Reserved for Future Use

    """

    expected_type = TreadmillData
    min_length: int = 2  # Flags only (all optional fields absent)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> TreadmillData:
        """Parse Treadmill Data from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            TreadmillData with all present fields populated.

        """
        flags = TreadmillDataFlags(DataParser.parse_int16(data, 0, signed=False))
        offset = 2

        # Bit 0 -- inverted: Instantaneous Speed present when bit is NOT set
        instantaneous_speed = None
        if not (flags & TreadmillDataFlags.MORE_DATA) and len(data) >= offset + 2:
            raw_speed = DataParser.parse_int16(data, offset, signed=False)
            instantaneous_speed = raw_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 1 -- Average Speed
        average_speed = None
        if (flags & TreadmillDataFlags.AVERAGE_SPEED_PRESENT) and len(data) >= offset + 2:
            raw_avg_speed = DataParser.parse_int16(data, offset, signed=False)
            average_speed = raw_avg_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 2 -- Total Distance (uint24)
        total_distance = None
        if (flags & TreadmillDataFlags.TOTAL_DISTANCE_PRESENT) and len(data) >= offset + 3:
            total_distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        # Bit 3 -- Inclination (sint16) + Ramp Angle Setting (sint16)
        inclination = None
        ramp_angle_setting = None
        if (flags & TreadmillDataFlags.INCLINATION_AND_RAMP_PRESENT) and len(data) >= offset + 4:
            raw_incl = DataParser.parse_int16(data, offset, signed=True)
            inclination = raw_incl / _TENTH_RESOLUTION
            offset += 2
            raw_ramp = DataParser.parse_int16(data, offset, signed=True)
            ramp_angle_setting = raw_ramp / _TENTH_RESOLUTION
            offset += 2

        # Bit 4 -- Positive Elevation Gain (uint16) + Negative Elevation Gain (uint16)
        positive_elevation_gain = None
        negative_elevation_gain = None
        if (flags & TreadmillDataFlags.ELEVATION_GAIN_PRESENT) and len(data) >= offset + 4:
            raw_pos = DataParser.parse_int16(data, offset, signed=False)
            positive_elevation_gain = raw_pos / _TENTH_RESOLUTION
            offset += 2
            raw_neg = DataParser.parse_int16(data, offset, signed=False)
            negative_elevation_gain = raw_neg / _TENTH_RESOLUTION
            offset += 2

        # Bit 5 -- Instantaneous Pace
        instantaneous_pace = None
        if (flags & TreadmillDataFlags.INSTANTANEOUS_PACE_PRESENT) and len(data) >= offset + 2:
            instantaneous_pace = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 6 -- Average Pace
        average_pace = None
        if (flags & TreadmillDataFlags.AVERAGE_PACE_PRESENT) and len(data) >= offset + 2:
            average_pace = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 7 -- Energy triplet (Total + Per Hour + Per Minute)
        total_energy = None
        energy_per_hour = None
        energy_per_minute = None
        if flags & TreadmillDataFlags.EXPENDED_ENERGY_PRESENT:
            total_energy, energy_per_hour, energy_per_minute, offset = decode_energy_triplet(data, offset)

        # Bit 8 -- Heart Rate
        heart_rate = None
        if flags & TreadmillDataFlags.HEART_RATE_PRESENT:
            heart_rate, offset = decode_heart_rate(data, offset)

        # Bit 9 -- Metabolic Equivalent
        metabolic_equivalent = None
        if flags & TreadmillDataFlags.METABOLIC_EQUIVALENT_PRESENT:
            metabolic_equivalent, offset = decode_metabolic_equivalent(data, offset)

        # Bit 10 -- Elapsed Time
        elapsed_time = None
        if flags & TreadmillDataFlags.ELAPSED_TIME_PRESENT:
            elapsed_time, offset = decode_elapsed_time(data, offset)

        # Bit 11 -- Remaining Time
        remaining_time = None
        if flags & TreadmillDataFlags.REMAINING_TIME_PRESENT:
            remaining_time, offset = decode_remaining_time(data, offset)

        # Bit 12 -- Force On Belt (sint16) + Power Output (sint16)
        force_on_belt = None
        power_output = None
        if (flags & TreadmillDataFlags.FORCE_AND_POWER_PRESENT) and len(data) >= offset + 4:
            force_on_belt = DataParser.parse_int16(data, offset, signed=True)
            offset += 2
            power_output = DataParser.parse_int16(data, offset, signed=True)
            offset += 2

        return TreadmillData(
            flags=flags,
            instantaneous_speed=instantaneous_speed,
            average_speed=average_speed,
            total_distance=total_distance,
            inclination=inclination,
            ramp_angle_setting=ramp_angle_setting,
            positive_elevation_gain=positive_elevation_gain,
            negative_elevation_gain=negative_elevation_gain,
            instantaneous_pace=instantaneous_pace,
            average_pace=average_pace,
            total_energy=total_energy,
            energy_per_hour=energy_per_hour,
            energy_per_minute=energy_per_minute,
            heart_rate=heart_rate,
            metabolic_equivalent=metabolic_equivalent,
            elapsed_time=elapsed_time,
            remaining_time=remaining_time,
            force_on_belt=force_on_belt,
            power_output=power_output,
        )

    def _encode_value(self, data: TreadmillData) -> bytearray:  # noqa: PLR0912
        """Encode TreadmillData back to BLE bytes.

        Reconstructs flags from present fields so round-trip encoding
        preserves the original wire format.

        Args:
            data: TreadmillData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = TreadmillDataFlags(0)

        # Bit 0 -- inverted: set MORE_DATA when Speed is absent
        if data.instantaneous_speed is None:
            flags |= TreadmillDataFlags.MORE_DATA
        if data.average_speed is not None:
            flags |= TreadmillDataFlags.AVERAGE_SPEED_PRESENT
        if data.total_distance is not None:
            flags |= TreadmillDataFlags.TOTAL_DISTANCE_PRESENT
        if data.inclination is not None:
            flags |= TreadmillDataFlags.INCLINATION_AND_RAMP_PRESENT
        if data.positive_elevation_gain is not None:
            flags |= TreadmillDataFlags.ELEVATION_GAIN_PRESENT
        if data.instantaneous_pace is not None:
            flags |= TreadmillDataFlags.INSTANTANEOUS_PACE_PRESENT
        if data.average_pace is not None:
            flags |= TreadmillDataFlags.AVERAGE_PACE_PRESENT
        if data.total_energy is not None:
            flags |= TreadmillDataFlags.EXPENDED_ENERGY_PRESENT
        if data.heart_rate is not None:
            flags |= TreadmillDataFlags.HEART_RATE_PRESENT
        if data.metabolic_equivalent is not None:
            flags |= TreadmillDataFlags.METABOLIC_EQUIVALENT_PRESENT
        if data.elapsed_time is not None:
            flags |= TreadmillDataFlags.ELAPSED_TIME_PRESENT
        if data.remaining_time is not None:
            flags |= TreadmillDataFlags.REMAINING_TIME_PRESENT
        if data.force_on_belt is not None:
            flags |= TreadmillDataFlags.FORCE_AND_POWER_PRESENT

        result = DataParser.encode_int16(int(flags), signed=False)

        if data.instantaneous_speed is not None:
            raw_speed = round(data.instantaneous_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_speed, signed=False))
        if data.average_speed is not None:
            raw_avg_speed = round(data.average_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_avg_speed, signed=False))
        if data.total_distance is not None:
            result.extend(DataParser.encode_int24(data.total_distance, signed=False))
        if data.inclination is not None:
            raw_incl = round(data.inclination * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_incl, signed=True))
        if data.ramp_angle_setting is not None:
            raw_ramp = round(data.ramp_angle_setting * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_ramp, signed=True))
        if data.positive_elevation_gain is not None:
            raw_pos = round(data.positive_elevation_gain * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_pos, signed=False))
        if data.negative_elevation_gain is not None:
            raw_neg = round(data.negative_elevation_gain * _TENTH_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_neg, signed=False))
        if data.instantaneous_pace is not None:
            result.extend(DataParser.encode_int16(data.instantaneous_pace, signed=False))
        if data.average_pace is not None:
            result.extend(DataParser.encode_int16(data.average_pace, signed=False))
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
        if data.force_on_belt is not None:
            result.extend(DataParser.encode_int16(data.force_on_belt, signed=True))
        if data.power_output is not None:
            result.extend(DataParser.encode_int16(data.power_output, signed=True))

        return result
