"""Position Quality characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.location import PositionStatus
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class PositionQualityFlags(IntFlag):
    """Position Quality flags as per Bluetooth SIG specification."""

    NUMBER_OF_BEACONS_IN_SOLUTION_PRESENT = 0x0001
    NUMBER_OF_BEACONS_IN_VIEW_PRESENT = 0x0002
    TIME_TO_FIRST_FIX_PRESENT = 0x0004
    EHPE_PRESENT = 0x0008
    EVPE_PRESENT = 0x0010
    HDOP_PRESENT = 0x0020
    VDOP_PRESENT = 0x0040


class PositionQualityData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Position Quality characteristic."""

    flags: PositionQualityFlags
    number_of_beacons_in_solution: int | None = None
    number_of_beacons_in_view: int | None = None
    time_to_first_fix: float | None = None
    ehpe: float | None = None
    evpe: float | None = None
    hdop: float | None = None
    vdop: float | None = None
    position_status: PositionStatus | None = None


class PositionQualityCharacteristic(BaseCharacteristic[PositionQualityData]):
    """Position Quality characteristic.

    Used to represent data related to the quality of a position measurement.
    """

    _python_type: type | str | None = dict  # Override since decode_value returns dataclass

    min_length = 2  # Flags(2) minimum
    max_length = 16  # Flags(2) + NumberOfBeaconsInSolution(1) + NumberOfBeaconsInView(1) +
    # TimeToFirstFix(2) + EHPE(4) + EVPE(4) + HDOP(1) + VDOP(1) maximum
    allow_variable_length: bool = True  # Variable optional fields

    # Bit masks and shifts for status information in flags
    POSITION_STATUS_MASK = 0x0180
    POSITION_STATUS_SHIFT = 7

    # Maximum valid enum value for PositionStatus
    _MAX_POSITION_STATUS_VALUE = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PositionQualityData:  # pylint: disable=too-many-locals
        """Parse position quality data according to Bluetooth specification.

        Format: Flags(2) + [Number of Beacons in Solution(1)] + [Number of Beacons in View(1)] +
        [Time to First Fix(2)] + [EHPE(4)] + [EVPE(4)] + [HDOP(1)] + [VDOP(1)].

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing surrounding context (may be None)
            validate: Whether to validate ranges (default True)

        Returns:
            PositionQualityData containing parsed position quality data

        """
        flags = PositionQualityFlags(DataParser.parse_int16(data, 0, signed=False))

        # Extract status information from flags
        position_status_bits = (flags & self.POSITION_STATUS_MASK) >> self.POSITION_STATUS_SHIFT
        position_status = (
            PositionStatus(position_status_bits) if position_status_bits <= self._MAX_POSITION_STATUS_VALUE else None
        )

        # Parse optional fields
        number_of_beacons_in_solution: int | None = None
        number_of_beacons_in_view: int | None = None
        time_to_first_fix: float | None = None
        ehpe: float | None = None
        evpe: float | None = None
        hdop: float | None = None
        vdop: float | None = None
        offset = 2

        if (flags & PositionQualityFlags.NUMBER_OF_BEACONS_IN_SOLUTION_PRESENT) and len(data) >= offset + 1:
            number_of_beacons_in_solution = data[offset]
            offset += 1

        if (flags & PositionQualityFlags.NUMBER_OF_BEACONS_IN_VIEW_PRESENT) and len(data) >= offset + 1:
            number_of_beacons_in_view = data[offset]
            offset += 1

        if (flags & PositionQualityFlags.TIME_TO_FIRST_FIX_PRESENT) and len(data) >= offset + 2:
            # Unit is 1/10 seconds
            time_to_first_fix = DataParser.parse_int16(data, offset, signed=False) / 10.0
            offset += 2

        if (flags & PositionQualityFlags.EHPE_PRESENT) and len(data) >= offset + 4:
            # Unit is 1/100 m
            ehpe = DataParser.parse_int32(data, offset, signed=False) / 100.0
            offset += 4

        if (flags & PositionQualityFlags.EVPE_PRESENT) and len(data) >= offset + 4:
            # Unit is 1/100 m
            evpe = DataParser.parse_int32(data, offset, signed=False) / 100.0
            offset += 4

        if (flags & PositionQualityFlags.HDOP_PRESENT) and len(data) >= offset + 1:
            # Unit is 2*10^-1
            hdop = data[offset] / 2.0
            offset += 1

        if (flags & PositionQualityFlags.VDOP_PRESENT) and len(data) >= offset + 1:
            # Unit is 2*10^-1
            vdop = data[offset] / 2.0

        return PositionQualityData(
            flags=flags,
            number_of_beacons_in_solution=number_of_beacons_in_solution,
            number_of_beacons_in_view=number_of_beacons_in_view,
            time_to_first_fix=time_to_first_fix,
            ehpe=ehpe,
            evpe=evpe,
            hdop=hdop,
            vdop=vdop,
            position_status=position_status,
        )

    def _encode_value(self, data: PositionQualityData) -> bytearray:
        """Encode PositionQualityData back to bytes.

        Args:
            data: PositionQualityData instance to encode

        Returns:
            Encoded bytes representing the position quality data

        """
        result = bytearray()

        flags = int(data.flags)

        # Set status bits in flags
        if data.position_status is not None:
            flags |= data.position_status.value << self.POSITION_STATUS_SHIFT

        result.extend(DataParser.encode_int16(flags, signed=False))

        if data.number_of_beacons_in_solution is not None:
            result.append(data.number_of_beacons_in_solution)

        if data.number_of_beacons_in_view is not None:
            result.append(data.number_of_beacons_in_view)

        if data.time_to_first_fix is not None:
            time_value = int(data.time_to_first_fix * 10)
            result.extend(DataParser.encode_int16(time_value, signed=False))

        if data.ehpe is not None:
            ehpe_value = int(data.ehpe * 100)
            result.extend(DataParser.encode_int32(ehpe_value, signed=False))

        if data.evpe is not None:
            evpe_value = int(data.evpe * 100)
            result.extend(DataParser.encode_int32(evpe_value, signed=False))

        if data.hdop is not None:
            hdop_value = int(data.hdop * 2)
            result.append(hdop_value)

        if data.vdop is not None:
            vdop_value = int(data.vdop * 2)
            result.append(vdop_value)

        return result
