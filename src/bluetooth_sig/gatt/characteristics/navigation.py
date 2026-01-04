"""Navigation characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum, IntFlag

import msgspec

from ...types.gatt_enums import ValueType
from ...types.location import PositionStatus
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class NavigationFlags(IntFlag):
    """Navigation flags as per Bluetooth SIG specification."""

    REMAINING_DISTANCE_PRESENT = 0x0001
    REMAINING_VERTICAL_DISTANCE_PRESENT = 0x0002
    ESTIMATED_TIME_OF_ARRIVAL_PRESENT = 0x0004


class NavigationIndicatorType(IntEnum):
    """Navigation indicator type enumeration."""

    TO_WAYPOINT = 0
    TO_DESTINATION = 1


class NavigationData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Navigation characteristic."""

    flags: NavigationFlags
    bearing: float
    heading: float
    remaining_distance: float | None = None
    remaining_vertical_distance: float | None = None
    estimated_time_of_arrival: datetime | None = None
    position_status: PositionStatus | None = None
    heading_source: HeadingSource | None = None
    navigation_indicator_type: NavigationIndicatorType | None = None
    waypoint_reached: bool | None = None
    destination_reached: bool | None = None


class HeadingSource(IntEnum):
    """Heading source enumeration."""

    HEADING_BASED_ON_MOVEMENT = 0
    HEADING_BASED_ON_MAGNETIC_COMPASS = 1


class NavigationCharacteristic(BaseCharacteristic[NavigationData]):
    """Navigation characteristic.

    Used to represent data related to a navigation sensor.
    """

    _manual_value_type: ValueType | str | None = ValueType.DICT  # Override since decode_value returns dataclass

    min_length = 6  # Flags(2) + Bearing(2) + Heading(2) minimum
    max_length = 16  # + RemainingDistance(3) + RemainingVerticalDistance(3) + EstimatedTimeOfArrival(7) maximum
    allow_variable_length: bool = True  # Variable optional fields

    # Bit masks and shifts for status information in flags
    POSITION_STATUS_MASK = 0x0006
    POSITION_STATUS_SHIFT = 1
    HEADING_SOURCE_MASK = 0x0020
    HEADING_SOURCE_SHIFT = 5
    NAVIGATION_INDICATOR_TYPE_MASK = 0x0040
    NAVIGATION_INDICATOR_TYPE_SHIFT = 6
    WAYPOINT_REACHED_MASK = 0x0080
    DESTINATION_REACHED_MASK = 0x0100

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> NavigationData:  # pylint: disable=too-many-locals
        """Parse navigation data according to Bluetooth specification.

        Format: Flags(2) + Bearing(2) + Heading(2) + [Remaining Distance(3)] +
        [Remaining Vertical Distance(3)] + [Estimated Time of Arrival(7)].

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing surrounding context (may be None)

        Returns:
            NavigationData containing parsed navigation data

        """
        if len(data) < 6:
            raise ValueError("Navigation data must be at least 6 bytes")

        flags = NavigationFlags(DataParser.parse_int16(data, 0, signed=False))

        # Unit is 1*10^-2 degrees
        bearing = DataParser.parse_int16(data, 2, signed=False) / 100.0
        heading = DataParser.parse_int16(data, 4, signed=False) / 100.0

        # Extract status information from flags
        position_status_bits = (flags & self.POSITION_STATUS_MASK) >> self.POSITION_STATUS_SHIFT
        position_status = PositionStatus(position_status_bits) if position_status_bits <= 3 else None

        heading_source_bit = (flags & self.HEADING_SOURCE_MASK) >> self.HEADING_SOURCE_SHIFT
        heading_source = HeadingSource(heading_source_bit)

        navigation_indicator_type_bit = (
            flags & self.NAVIGATION_INDICATOR_TYPE_MASK
        ) >> self.NAVIGATION_INDICATOR_TYPE_SHIFT
        navigation_indicator_type = NavigationIndicatorType(navigation_indicator_type_bit)

        waypoint_reached = bool(flags & self.WAYPOINT_REACHED_MASK)
        destination_reached = bool(flags & self.DESTINATION_REACHED_MASK)

        # Parse optional fields
        remaining_distance: float | None = None
        remaining_vertical_distance: float | None = None
        estimated_time_of_arrival: datetime | None = None
        offset = 6

        if (flags & NavigationFlags.REMAINING_DISTANCE_PRESENT) and len(data) >= offset + 3:
            # Unit is 1/10 m
            remaining_distance = DataParser.parse_int24(data, offset, signed=False) / 10.0
            offset += 3

        if (flags & NavigationFlags.REMAINING_VERTICAL_DISTANCE_PRESENT) and len(data) >= offset + 3:
            # Unit is 1/100 m
            remaining_vertical_distance = DataParser.parse_int24(data, offset, signed=True) / 100.0
            offset += 3

        if (flags & NavigationFlags.ESTIMATED_TIME_OF_ARRIVAL_PRESENT) and len(data) >= offset + 7:
            estimated_time_of_arrival = IEEE11073Parser.parse_timestamp(data, offset)

        return NavigationData(
            flags=flags,
            bearing=bearing,
            heading=heading,
            remaining_distance=remaining_distance,
            remaining_vertical_distance=remaining_vertical_distance,
            estimated_time_of_arrival=estimated_time_of_arrival,
            position_status=position_status,
            heading_source=heading_source,
            navigation_indicator_type=navigation_indicator_type,
            waypoint_reached=waypoint_reached,
            destination_reached=destination_reached,
        )

    def _encode_value(self, data: NavigationData) -> bytearray:
        """Encode NavigationData back to bytes.

        Args:
            data: NavigationData instance to encode

        Returns:
            Encoded bytes representing the navigation data

        """
        result = bytearray()

        flags = int(data.flags)

        # Set status bits in flags
        if data.position_status is not None:
            flags |= data.position_status.value << self.POSITION_STATUS_SHIFT

        if data.heading_source is not None:
            flags |= data.heading_source.value << self.HEADING_SOURCE_SHIFT

        if data.navigation_indicator_type is not None:
            flags |= data.navigation_indicator_type.value << self.NAVIGATION_INDICATOR_TYPE_SHIFT

        if data.waypoint_reached is not None and data.waypoint_reached:
            flags |= self.WAYPOINT_REACHED_MASK

        if data.destination_reached is not None and data.destination_reached:
            flags |= self.DESTINATION_REACHED_MASK

        result.extend(DataParser.encode_int16(flags, signed=False))

        # Unit is 1*10^-2 degrees
        bearing_value = int(data.bearing * 100)
        heading_value = int(data.heading * 100)
        result.extend(DataParser.encode_int16(bearing_value, signed=False))
        result.extend(DataParser.encode_int16(heading_value, signed=False))

        if data.remaining_distance is not None:
            distance_value = int(data.remaining_distance * 10)
            result.extend(DataParser.encode_int24(distance_value, signed=False))

        if data.remaining_vertical_distance is not None:
            vertical_distance_value = int(data.remaining_vertical_distance * 100)
            result.extend(DataParser.encode_int24(vertical_distance_value, signed=True))

        if data.estimated_time_of_arrival is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.estimated_time_of_arrival))

        return result
