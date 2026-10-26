"""Indoor Bike Data characteristic implementation.

Implements the Indoor Bike Data characteristic (0x2AD2) from the Fitness
Machine Service.  A 16-bit flags field controls the presence of optional
data fields.

Bit 0 ("More Data") uses **inverted logic**: when bit 0 is 0 the
Instantaneous Speed field IS present; when bit 0 is 1 it is absent.
All other bits use normal logic (1 = present).

References:
    Bluetooth SIG Fitness Machine Service 1.0
    org.bluetooth.characteristic.indoor_bike_data (GSS YAML)
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

# Cadence: M=1, d=0, b=-1 -> actual = raw / 2 rpm
_CADENCE_DIVISOR = 2.0

# Resistance level: M=1, d=1, b=0 -> actual = raw * 10
_RESISTANCE_RESOLUTION = 10.0


class IndoorBikeDataFlags(IntFlag):
    """Indoor Bike Data flags as per Bluetooth SIG specification.

    Bit 0 uses inverted logic: 0 = Instantaneous Speed present,
    1 = absent.
    """

    MORE_DATA = 0x0001  # Inverted: 0 -> Speed present, 1 -> absent
    AVERAGE_SPEED_PRESENT = 0x0002
    INSTANTANEOUS_CADENCE_PRESENT = 0x0004
    AVERAGE_CADENCE_PRESENT = 0x0008
    TOTAL_DISTANCE_PRESENT = 0x0010
    RESISTANCE_LEVEL_PRESENT = 0x0020
    INSTANTANEOUS_POWER_PRESENT = 0x0040
    AVERAGE_POWER_PRESENT = 0x0080
    EXPENDED_ENERGY_PRESENT = 0x0100
    HEART_RATE_PRESENT = 0x0200
    METABOLIC_EQUIVALENT_PRESENT = 0x0400
    ELAPSED_TIME_PRESENT = 0x0800
    REMAINING_TIME_PRESENT = 0x1000


class IndoorBikeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Indoor Bike Data characteristic.

    Attributes:
        flags: Raw 16-bit flags field.
        instantaneous_speed: Instantaneous speed in km/h (0.01 resolution).
        average_speed: Average speed in km/h (0.01 resolution).
        instantaneous_cadence: Instantaneous cadence in rpm (0.5 resolution).
        average_cadence: Average cadence in rpm (0.5 resolution).
        total_distance: Total distance in metres (uint24).
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

    """

    flags: IndoorBikeDataFlags
    instantaneous_speed: float | None = None
    average_speed: float | None = None
    instantaneous_cadence: float | None = None
    average_cadence: float | None = None
    total_distance: int | None = None
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
        if (
            self.instantaneous_cadence is not None
            and not 0.0 <= self.instantaneous_cadence <= UINT16_MAX / _CADENCE_DIVISOR
        ):
            raise ValueError(
                f"Instantaneous cadence must be 0.0-{UINT16_MAX / _CADENCE_DIVISOR}, got {self.instantaneous_cadence}"
            )
        if self.average_cadence is not None and not 0.0 <= self.average_cadence <= UINT16_MAX / _CADENCE_DIVISOR:
            raise ValueError(f"Average cadence must be 0.0-{UINT16_MAX / _CADENCE_DIVISOR}, got {self.average_cadence}")
        if self.total_distance is not None and not 0 <= self.total_distance <= UINT24_MAX:
            raise ValueError(f"Total distance must be 0-{UINT24_MAX}, got {self.total_distance}")
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


class IndoorBikeDataCharacteristic(BaseCharacteristic[IndoorBikeData]):
    """Indoor Bike Data characteristic (0x2AD2).

    Used in the Fitness Machine Service to transmit indoor bike workout
    data.  A 16-bit flags field controls which optional fields are present.

    Flag-bit assignments (from GSS YAML):
        Bit 0: More Data -- **inverted**: 0 -> Inst. Speed present, 1 -> absent
        Bit 1: Average Speed present
        Bit 2: Instantaneous Cadence present
        Bit 3: Average Cadence present
        Bit 4: Total Distance present
        Bit 5: Resistance Level present
        Bit 6: Instantaneous Power present
        Bit 7: Average Power present
        Bit 8: Expended Energy present (gates triplet: total + /hr + /min)
        Bit 9: Heart Rate present
        Bit 10: Metabolic Equivalent present
        Bit 11: Elapsed Time present
        Bit 12: Remaining Time present
        Bits 13-15: Reserved for Future Use

    """

    expected_type = IndoorBikeData
    min_length: int = 2  # Flags only (all optional fields absent)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> IndoorBikeData:
        """Parse Indoor Bike Data from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            IndoorBikeData with all present fields populated.

        """
        flags = IndoorBikeDataFlags(DataParser.parse_int16(data, 0, signed=False))
        offset = 2

        # Bit 0 -- inverted: Instantaneous Speed present when bit is NOT set
        instantaneous_speed = None
        if not (flags & IndoorBikeDataFlags.MORE_DATA) and len(data) >= offset + 2:
            raw_speed = DataParser.parse_int16(data, offset, signed=False)
            instantaneous_speed = raw_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 1 -- Average Speed
        average_speed = None
        if (flags & IndoorBikeDataFlags.AVERAGE_SPEED_PRESENT) and len(data) >= offset + 2:
            raw_avg_speed = DataParser.parse_int16(data, offset, signed=False)
            average_speed = raw_avg_speed / _SPEED_RESOLUTION
            offset += 2

        # Bit 2 -- Instantaneous Cadence
        instantaneous_cadence = None
        if (flags & IndoorBikeDataFlags.INSTANTANEOUS_CADENCE_PRESENT) and len(data) >= offset + 2:
            raw_cadence = DataParser.parse_int16(data, offset, signed=False)
            instantaneous_cadence = raw_cadence / _CADENCE_DIVISOR
            offset += 2

        # Bit 3 -- Average Cadence
        average_cadence = None
        if (flags & IndoorBikeDataFlags.AVERAGE_CADENCE_PRESENT) and len(data) >= offset + 2:
            raw_avg_cadence = DataParser.parse_int16(data, offset, signed=False)
            average_cadence = raw_avg_cadence / _CADENCE_DIVISOR
            offset += 2

        # Bit 4 -- Total Distance (uint24)
        total_distance = None
        if (flags & IndoorBikeDataFlags.TOTAL_DISTANCE_PRESENT) and len(data) >= offset + 3:
            total_distance = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        # Bit 5 -- Resistance Level
        resistance_level = None
        if (flags & IndoorBikeDataFlags.RESISTANCE_LEVEL_PRESENT) and len(data) >= offset + 1:
            raw_resistance = DataParser.parse_int8(data, offset, signed=False)
            resistance_level = raw_resistance * _RESISTANCE_RESOLUTION
            offset += 1

        # Bit 6 -- Instantaneous Power (sint16)
        instantaneous_power = None
        if (flags & IndoorBikeDataFlags.INSTANTANEOUS_POWER_PRESENT) and len(data) >= offset + 2:
            instantaneous_power = DataParser.parse_int16(data, offset, signed=True)
            offset += 2

        # Bit 7 -- Average Power (sint16)
        average_power = None
        if (flags & IndoorBikeDataFlags.AVERAGE_POWER_PRESENT) and len(data) >= offset + 2:
            average_power = DataParser.parse_int16(data, offset, signed=True)
            offset += 2

        # Bit 8 -- Energy triplet (Total + Per Hour + Per Minute)
        total_energy = None
        energy_per_hour = None
        energy_per_minute = None
        if flags & IndoorBikeDataFlags.EXPENDED_ENERGY_PRESENT:
            total_energy, energy_per_hour, energy_per_minute, offset = decode_energy_triplet(data, offset)

        # Bit 9 -- Heart Rate
        heart_rate = None
        if flags & IndoorBikeDataFlags.HEART_RATE_PRESENT:
            heart_rate, offset = decode_heart_rate(data, offset)

        # Bit 10 -- Metabolic Equivalent
        metabolic_equivalent = None
        if flags & IndoorBikeDataFlags.METABOLIC_EQUIVALENT_PRESENT:
            metabolic_equivalent, offset = decode_metabolic_equivalent(data, offset)

        # Bit 11 -- Elapsed Time
        elapsed_time = None
        if flags & IndoorBikeDataFlags.ELAPSED_TIME_PRESENT:
            elapsed_time, offset = decode_elapsed_time(data, offset)

        # Bit 12 -- Remaining Time
        remaining_time = None
        if flags & IndoorBikeDataFlags.REMAINING_TIME_PRESENT:
            remaining_time, offset = decode_remaining_time(data, offset)

        return IndoorBikeData(
            flags=flags,
            instantaneous_speed=instantaneous_speed,
            average_speed=average_speed,
            instantaneous_cadence=instantaneous_cadence,
            average_cadence=average_cadence,
            total_distance=total_distance,
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
        )

    def _encode_value(self, data: IndoorBikeData) -> bytearray:  # noqa: PLR0912
        """Encode IndoorBikeData back to BLE bytes.

        Reconstructs flags from present fields so round-trip encoding
        preserves the original wire format.

        Args:
            data: IndoorBikeData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = IndoorBikeDataFlags(0)

        # Bit 0 -- inverted: set MORE_DATA when Speed is absent
        if data.instantaneous_speed is None:
            flags |= IndoorBikeDataFlags.MORE_DATA
        if data.average_speed is not None:
            flags |= IndoorBikeDataFlags.AVERAGE_SPEED_PRESENT
        if data.instantaneous_cadence is not None:
            flags |= IndoorBikeDataFlags.INSTANTANEOUS_CADENCE_PRESENT
        if data.average_cadence is not None:
            flags |= IndoorBikeDataFlags.AVERAGE_CADENCE_PRESENT
        if data.total_distance is not None:
            flags |= IndoorBikeDataFlags.TOTAL_DISTANCE_PRESENT
        if data.resistance_level is not None:
            flags |= IndoorBikeDataFlags.RESISTANCE_LEVEL_PRESENT
        if data.instantaneous_power is not None:
            flags |= IndoorBikeDataFlags.INSTANTANEOUS_POWER_PRESENT
        if data.average_power is not None:
            flags |= IndoorBikeDataFlags.AVERAGE_POWER_PRESENT
        if data.total_energy is not None:
            flags |= IndoorBikeDataFlags.EXPENDED_ENERGY_PRESENT
        if data.heart_rate is not None:
            flags |= IndoorBikeDataFlags.HEART_RATE_PRESENT
        if data.metabolic_equivalent is not None:
            flags |= IndoorBikeDataFlags.METABOLIC_EQUIVALENT_PRESENT
        if data.elapsed_time is not None:
            flags |= IndoorBikeDataFlags.ELAPSED_TIME_PRESENT
        if data.remaining_time is not None:
            flags |= IndoorBikeDataFlags.REMAINING_TIME_PRESENT

        result = DataParser.encode_int16(int(flags), signed=False)

        if data.instantaneous_speed is not None:
            raw_speed = round(data.instantaneous_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_speed, signed=False))
        if data.average_speed is not None:
            raw_avg_speed = round(data.average_speed * _SPEED_RESOLUTION)
            result.extend(DataParser.encode_int16(raw_avg_speed, signed=False))
        if data.instantaneous_cadence is not None:
            raw_cadence = round(data.instantaneous_cadence * _CADENCE_DIVISOR)
            result.extend(DataParser.encode_int16(raw_cadence, signed=False))
        if data.average_cadence is not None:
            raw_avg_cadence = round(data.average_cadence * _CADENCE_DIVISOR)
            result.extend(DataParser.encode_int16(raw_avg_cadence, signed=False))
        if data.total_distance is not None:
            result.extend(DataParser.encode_int24(data.total_distance, signed=False))
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
