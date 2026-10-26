"""Stair Climber Data characteristic implementation.

Implements the Stair Climber Data characteristic (0x2AD0) from the Fitness
Machine Service.  A 16-bit flags field controls the presence of optional
data fields.

Bit 0 ("More Data") uses **inverted logic**: when bit 0 is 0 the Floors
field IS present; when bit 0 is 1 it is absent.  All other bits use normal
logic (1 = present).

References:
    Bluetooth SIG Fitness Machine Service 1.0
    org.bluetooth.characteristic.stair_climber_data (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
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


class StairClimberDataFlags(IntFlag):
    """Stair Climber Data flags as per Bluetooth SIG specification.

    Bit 0 uses inverted logic: 0 = Floors present, 1 = Floors absent.
    """

    MORE_DATA = 0x0001  # Inverted: 0 -> Floors present, 1 -> absent
    STEPS_PER_MINUTE_PRESENT = 0x0002
    AVERAGE_STEP_RATE_PRESENT = 0x0004
    POSITIVE_ELEVATION_GAIN_PRESENT = 0x0008
    STRIDE_COUNT_PRESENT = 0x0010
    EXPENDED_ENERGY_PRESENT = 0x0020
    HEART_RATE_PRESENT = 0x0040
    METABOLIC_EQUIVALENT_PRESENT = 0x0080
    ELAPSED_TIME_PRESENT = 0x0100
    REMAINING_TIME_PRESENT = 0x0200


class StairClimberData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Stair Climber Data characteristic.

    Attributes:
        flags: Raw 16-bit flags field.
        floors: Total floors counted (present when bit 0 is 0).
        steps_per_minute: Step rate in steps/min.
        average_step_rate: Average step rate in steps/min.
        positive_elevation_gain: Positive elevation gain in metres.
        stride_count: Total strides since session start.
        total_energy: Total expended energy in kcal.
        energy_per_hour: Expended energy per hour in kcal.
        energy_per_minute: Expended energy per minute in kcal.
        heart_rate: Heart rate in bpm.
        metabolic_equivalent: MET value (0.1 resolution).
        elapsed_time: Elapsed time in seconds.
        remaining_time: Remaining time in seconds.

    """

    flags: StairClimberDataFlags
    floors: int | None = None
    steps_per_minute: int | None = None
    average_step_rate: int | None = None
    positive_elevation_gain: int | None = None
    stride_count: int | None = None
    total_energy: int | None = None
    energy_per_hour: int | None = None
    energy_per_minute: int | None = None
    heart_rate: int | None = None
    metabolic_equivalent: float | None = None
    elapsed_time: int | None = None
    remaining_time: int | None = None

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if self.floors is not None and not 0 <= self.floors <= UINT16_MAX:
            raise ValueError(f"Floors must be 0-{UINT16_MAX}, got {self.floors}")
        if self.steps_per_minute is not None and not 0 <= self.steps_per_minute <= UINT16_MAX:
            raise ValueError(f"Steps per minute must be 0-{UINT16_MAX}, got {self.steps_per_minute}")
        if self.average_step_rate is not None and not 0 <= self.average_step_rate <= UINT16_MAX:
            raise ValueError(f"Average step rate must be 0-{UINT16_MAX}, got {self.average_step_rate}")
        if self.positive_elevation_gain is not None and not 0 <= self.positive_elevation_gain <= UINT16_MAX:
            raise ValueError(f"Positive elevation gain must be 0-{UINT16_MAX}, got {self.positive_elevation_gain}")
        if self.stride_count is not None and not 0 <= self.stride_count <= UINT16_MAX:
            raise ValueError(f"Stride count must be 0-{UINT16_MAX}, got {self.stride_count}")
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


class StairClimberDataCharacteristic(BaseCharacteristic[StairClimberData]):
    """Stair Climber Data characteristic (0x2AD0).

    Used in the Fitness Machine Service to transmit stair climber workout
    data.  A 16-bit flags field controls which optional fields are present.

    Flag-bit assignments (from GSS YAML):
        Bit 0: More Data -- **inverted**: 0 -> Floors present, 1 -> absent
        Bit 1: Steps Per Minute present
        Bit 2: Average Step Rate present
        Bit 3: Positive Elevation Gain present
        Bit 4: Stride Count present
        Bit 5: Expended Energy present (gates triplet: total + /hr + /min)
        Bit 6: Heart Rate present
        Bit 7: Metabolic Equivalent present
        Bit 8: Elapsed Time present
        Bit 9: Remaining Time present
        Bits 10-15: Reserved for Future Use

    """

    expected_type = StairClimberData
    min_length: int = 2  # Flags only (all optional fields absent)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> StairClimberData:
        """Parse Stair Climber Data from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            StairClimberData with all present fields populated.

        """
        flags = StairClimberDataFlags(DataParser.parse_int16(data, 0, signed=False))
        offset = 2

        # Bit 0 -- inverted: Floors present when bit is NOT set
        floors = None
        if not (flags & StairClimberDataFlags.MORE_DATA) and len(data) >= offset + 2:
            floors = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 1 -- Steps Per Minute
        steps_per_minute = None
        if (flags & StairClimberDataFlags.STEPS_PER_MINUTE_PRESENT) and len(data) >= offset + 2:
            steps_per_minute = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 2 -- Average Step Rate
        average_step_rate = None
        if (flags & StairClimberDataFlags.AVERAGE_STEP_RATE_PRESENT) and len(data) >= offset + 2:
            average_step_rate = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 3 -- Positive Elevation Gain
        positive_elevation_gain = None
        if (flags & StairClimberDataFlags.POSITIVE_ELEVATION_GAIN_PRESENT) and len(data) >= offset + 2:
            positive_elevation_gain = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 4 -- Stride Count
        stride_count = None
        if (flags & StairClimberDataFlags.STRIDE_COUNT_PRESENT) and len(data) >= offset + 2:
            stride_count = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Bit 5 -- Energy triplet (Total + Per Hour + Per Minute)
        total_energy = None
        energy_per_hour = None
        energy_per_minute = None
        if flags & StairClimberDataFlags.EXPENDED_ENERGY_PRESENT:
            total_energy, energy_per_hour, energy_per_minute, offset = decode_energy_triplet(data, offset)

        # Bit 6 -- Heart Rate
        heart_rate = None
        if flags & StairClimberDataFlags.HEART_RATE_PRESENT:
            heart_rate, offset = decode_heart_rate(data, offset)

        # Bit 7 -- Metabolic Equivalent
        metabolic_equivalent = None
        if flags & StairClimberDataFlags.METABOLIC_EQUIVALENT_PRESENT:
            metabolic_equivalent, offset = decode_metabolic_equivalent(data, offset)

        # Bit 8 -- Elapsed Time
        elapsed_time = None
        if flags & StairClimberDataFlags.ELAPSED_TIME_PRESENT:
            elapsed_time, offset = decode_elapsed_time(data, offset)

        # Bit 9 -- Remaining Time
        remaining_time = None
        if flags & StairClimberDataFlags.REMAINING_TIME_PRESENT:
            remaining_time, offset = decode_remaining_time(data, offset)

        return StairClimberData(
            flags=flags,
            floors=floors,
            steps_per_minute=steps_per_minute,
            average_step_rate=average_step_rate,
            positive_elevation_gain=positive_elevation_gain,
            stride_count=stride_count,
            total_energy=total_energy,
            energy_per_hour=energy_per_hour,
            energy_per_minute=energy_per_minute,
            heart_rate=heart_rate,
            metabolic_equivalent=metabolic_equivalent,
            elapsed_time=elapsed_time,
            remaining_time=remaining_time,
        )

    def _encode_value(self, data: StairClimberData) -> bytearray:
        """Encode StairClimberData back to BLE bytes.

        Reconstructs flags from present fields so round-trip encoding
        preserves the original wire format.

        Args:
            data: StairClimberData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = StairClimberDataFlags(0)

        # Bit 0 -- inverted: set MORE_DATA when Floors is absent
        if data.floors is None:
            flags |= StairClimberDataFlags.MORE_DATA
        if data.steps_per_minute is not None:
            flags |= StairClimberDataFlags.STEPS_PER_MINUTE_PRESENT
        if data.average_step_rate is not None:
            flags |= StairClimberDataFlags.AVERAGE_STEP_RATE_PRESENT
        if data.positive_elevation_gain is not None:
            flags |= StairClimberDataFlags.POSITIVE_ELEVATION_GAIN_PRESENT
        if data.stride_count is not None:
            flags |= StairClimberDataFlags.STRIDE_COUNT_PRESENT
        if data.total_energy is not None:
            flags |= StairClimberDataFlags.EXPENDED_ENERGY_PRESENT
        if data.heart_rate is not None:
            flags |= StairClimberDataFlags.HEART_RATE_PRESENT
        if data.metabolic_equivalent is not None:
            flags |= StairClimberDataFlags.METABOLIC_EQUIVALENT_PRESENT
        if data.elapsed_time is not None:
            flags |= StairClimberDataFlags.ELAPSED_TIME_PRESENT
        if data.remaining_time is not None:
            flags |= StairClimberDataFlags.REMAINING_TIME_PRESENT

        result = DataParser.encode_int16(int(flags), signed=False)

        if data.floors is not None:
            result.extend(DataParser.encode_int16(data.floors, signed=False))
        if data.steps_per_minute is not None:
            result.extend(DataParser.encode_int16(data.steps_per_minute, signed=False))
        if data.average_step_rate is not None:
            result.extend(DataParser.encode_int16(data.average_step_rate, signed=False))
        if data.positive_elevation_gain is not None:
            result.extend(DataParser.encode_int16(data.positive_elevation_gain, signed=False))
        if data.stride_count is not None:
            result.extend(DataParser.encode_int16(data.stride_count, signed=False))
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
