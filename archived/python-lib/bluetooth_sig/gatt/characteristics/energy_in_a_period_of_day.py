"""Energy in a Period of Day characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT24_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_TIME_DECIHOUR_RESOLUTION = 0.1  # Time Decihour 8: M=1, d=-1, b=0 -> 0.1 hr
# Energy: M=1, d=0, b=0 -> 1 kWh per raw uint24 unit


class EnergyInAPeriodOfDayData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for energy in a period of day.

    Energy value in kWh (integer, uint24) with a time-of-day range
    (0.1 hr resolution).
    """

    energy: int  # Energy in kWh (integer, uint24)
    start_time: float  # Start time in hours (0.1 hr resolution)
    end_time: float  # End time in hours (0.1 hr resolution)

    def __post_init__(self) -> None:
        """Validate data fields."""
        if not 0 <= self.energy <= UINT24_MAX:
            raise ValueError(f"Energy {self.energy} kWh is outside valid range (0 to {UINT24_MAX})")
        max_time = UINT8_MAX * _TIME_DECIHOUR_RESOLUTION
        for name, val in [("start_time", self.start_time), ("end_time", self.end_time)]:
            if not 0.0 <= val <= max_time:
                raise ValueError(f"{name} {val} hr is outside valid range (0.0 to {max_time})")


class EnergyInAPeriodOfDayCharacteristic(
    BaseCharacteristic[EnergyInAPeriodOfDayData],
):
    """Energy in a Period of Day characteristic (0x2AF3).

    org.bluetooth.characteristic.energy_in_a_period_of_day

    Represents an energy measurement within a time-of-day range. Fields:
    Energy (uint24, 1 kWh), start time (uint8, 0.1 hr),
    end time (uint8, 0.1 hr).
    """

    expected_length: int = 5  # uint24 + 2 x uint8
    min_length: int = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> EnergyInAPeriodOfDayData:
        """Parse energy in a period of day.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            EnergyInAPeriodOfDayData.

        """
        energy = DataParser.parse_int24(data, 0, signed=False)
        start_raw = DataParser.parse_int8(data, 3, signed=False)
        end_raw = DataParser.parse_int8(data, 4, signed=False)

        return EnergyInAPeriodOfDayData(
            energy=energy,
            start_time=start_raw * _TIME_DECIHOUR_RESOLUTION,
            end_time=end_raw * _TIME_DECIHOUR_RESOLUTION,
        )

    def _encode_value(self, data: EnergyInAPeriodOfDayData) -> bytearray:
        """Encode energy in a period of day.

        Args:
            data: EnergyInAPeriodOfDayData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        start_raw = round(data.start_time / _TIME_DECIHOUR_RESOLUTION)
        end_raw = round(data.end_time / _TIME_DECIHOUR_RESOLUTION)

        for name, value in [("start_time", start_raw), ("end_time", end_raw)]:
            if not 0 <= value <= UINT8_MAX:
                raise ValueError(f"{name} raw value {value} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int24(data.energy, signed=False))
        result.extend(DataParser.encode_int8(start_raw, signed=False))
        result.extend(DataParser.encode_int8(end_raw, signed=False))
        return result
