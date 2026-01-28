"""Location and Speed characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum, IntFlag

import msgspec

from ...types.gatt_enums import ValueType
from ...types.location import PositionStatus
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class LocationAndSpeedFlags(IntFlag):
    """Location and Speed flags as per Bluetooth SIG specification."""

    INSTANTANEOUS_SPEED_PRESENT = 0x0001
    TOTAL_DISTANCE_PRESENT = 0x0002
    LOCATION_PRESENT = 0x0004
    ELEVATION_PRESENT = 0x0008
    HEADING_PRESENT = 0x0010
    ROLLING_TIME_PRESENT = 0x0020
    UTC_TIME_PRESENT = 0x0040


class SpeedAndDistanceFormat(IntEnum):
    """Speed and distance format enumeration."""

    FORMAT_2D = 0
    FORMAT_3D = 1


class ElevationSource(IntEnum):
    """Elevation source enumeration."""

    POSITIONING_SYSTEM = 0
    BAROMETRIC_AIR_PRESSURE = 1
    DATABASE_SERVICE = 2
    OTHER = 3


class HeadingSource(IntEnum):
    """Heading source enumeration."""

    HEADING_BASED_ON_MOVEMENT = 0
    HEADING_BASED_ON_MAGNETIC_COMPASS = 1


class LocationAndSpeedData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Location and Speed characteristic."""

    flags: LocationAndSpeedFlags
    instantaneous_speed: float | None = None
    total_distance: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None
    heading: float | None = None
    rolling_time: int | None = None
    utc_time: datetime | None = None
    position_status: PositionStatus | None = None
    speed_and_distance_format: SpeedAndDistanceFormat | None = None
    elevation_source: ElevationSource | None = None
    heading_source: HeadingSource | None = None


class LocationAndSpeedCharacteristic(BaseCharacteristic[LocationAndSpeedData]):
    """Location and Speed characteristic.

    Used to represent data related to a location and speed sensor.
    Note that it is possible for this characteristic to exceed the default LE ATT_MTU size.
    """

    _manual_value_type: ValueType | str | None = ValueType.DICT  # Override since decode_value returns dataclass

    min_length = 2  # Flags(2) minimum
    max_length = 28  # Flags(2) + InstantaneousSpeed(2) + TotalDistance(3) + Location(8) +
    # Elevation(3) + Heading(2) + RollingTime(1) + UTCTime(7) maximum
    allow_variable_length: bool = True  # Variable optional fields

    # Bit masks and shifts for status information in flags
    POSITION_STATUS_MASK = 0x0300
    POSITION_STATUS_SHIFT = 8
    SPEED_DISTANCE_FORMAT_MASK = 0x0400
    SPEED_DISTANCE_FORMAT_SHIFT = 10
    ELEVATION_SOURCE_MASK = 0x1800
    ELEVATION_SOURCE_SHIFT = 11
    HEADING_SOURCE_MASK = 0x2000
    HEADING_SOURCE_SHIFT = 13

    # Maximum valid enum values
    _MAX_POSITION_STATUS_VALUE = 3
    _MAX_ELEVATION_SOURCE_VALUE = 3

    def _decode_value(  # pylint: disable=too-many-locals  # Location spec with many positional fields
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> LocationAndSpeedData:
        """Parse location and speed data according to Bluetooth specification.

        Format: Flags(2) + [Instantaneous Speed(2)] + [Total Distance(3)] + [Location - Latitude(4)] +
        [Location - Longitude(4)] + [Elevation(3)] + [Heading(2)] + [Rolling Time(1)] + [UTC Time(7)].

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing surrounding context (may be None)
            validate: Whether to validate ranges (default True)

        Returns:
            LocationAndSpeedData containing parsed location and speed data

        """
        flags = LocationAndSpeedFlags(DataParser.parse_int16(data, 0, signed=False))

        # Extract status information from flags
        position_status_bits = (flags & self.POSITION_STATUS_MASK) >> self.POSITION_STATUS_SHIFT
        position_status = (
            PositionStatus(position_status_bits) if position_status_bits <= self._MAX_POSITION_STATUS_VALUE else None
        )

        speed_distance_format_bit = (flags & self.SPEED_DISTANCE_FORMAT_MASK) >> self.SPEED_DISTANCE_FORMAT_SHIFT
        speed_and_distance_format = SpeedAndDistanceFormat(speed_distance_format_bit)

        elevation_source_bits = (flags & self.ELEVATION_SOURCE_MASK) >> self.ELEVATION_SOURCE_SHIFT
        elevation_source = (
            ElevationSource(elevation_source_bits)
            if elevation_source_bits <= self._MAX_ELEVATION_SOURCE_VALUE
            else None
        )

        heading_source_bit = (flags & self.HEADING_SOURCE_MASK) >> self.HEADING_SOURCE_SHIFT
        heading_source = HeadingSource(heading_source_bit)

        # Parse optional fields
        instantaneous_speed: float | None = None
        total_distance: float | None = None
        latitude: float | None = None
        longitude: float | None = None
        elevation: float | None = None
        heading: float | None = None
        rolling_time: int | None = None
        utc_time: datetime | None = None
        offset = 2

        if (flags & LocationAndSpeedFlags.INSTANTANEOUS_SPEED_PRESENT) and len(data) >= offset + 2:
            # Unit is 1/100 of a m/s
            instantaneous_speed = DataParser.parse_int16(data, offset, signed=False) / 100.0
            offset += 2

        if (flags & LocationAndSpeedFlags.TOTAL_DISTANCE_PRESENT) and len(data) >= offset + 3:
            # Unit is 1/10 m
            total_distance = DataParser.parse_int24(data, offset, signed=False) / 10.0
            offset += 3

        if (flags & LocationAndSpeedFlags.LOCATION_PRESENT) and len(data) >= offset + 8:
            # Unit is 1*10^-7 degrees
            latitude = DataParser.parse_int32(data, offset, signed=True) / 10000000.0
            longitude = DataParser.parse_int32(data, offset + 4, signed=True) / 10000000.0
            offset += 8

        if (flags & LocationAndSpeedFlags.ELEVATION_PRESENT) and len(data) >= offset + 3:
            # Unit is 1/100 m
            elevation = DataParser.parse_int24(data, offset, signed=True) / 100.0
            offset += 3

        if (flags & LocationAndSpeedFlags.HEADING_PRESENT) and len(data) >= offset + 2:
            # Unit is 1*10^-2 degrees
            heading = DataParser.parse_int16(data, offset, signed=False) / 100.0
            offset += 2

        if (flags & LocationAndSpeedFlags.ROLLING_TIME_PRESENT) and len(data) >= offset + 1:
            rolling_time = data[offset]
            offset += 1

        if (flags & LocationAndSpeedFlags.UTC_TIME_PRESENT) and len(data) >= offset + 7:
            utc_time = IEEE11073Parser.parse_timestamp(data, offset)

        return LocationAndSpeedData(
            flags=flags,
            instantaneous_speed=instantaneous_speed,
            total_distance=total_distance,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            heading=heading,
            rolling_time=rolling_time,
            utc_time=utc_time,
            position_status=position_status,
            speed_and_distance_format=speed_and_distance_format,
            elevation_source=elevation_source,
            heading_source=heading_source,
        )

    def _encode_value(self, data: LocationAndSpeedData) -> bytearray:
        """Encode LocationAndSpeedData back to bytes.

        Args:
            data: LocationAndSpeedData instance to encode

        Returns:
            Encoded bytes representing the location and speed data

        """
        result = bytearray()

        flags = int(data.flags)

        # Set status bits in flags
        if data.position_status is not None:
            flags |= data.position_status.value << self.POSITION_STATUS_SHIFT

        if data.speed_and_distance_format is not None:
            flags |= data.speed_and_distance_format.value << self.SPEED_DISTANCE_FORMAT_SHIFT

        if data.elevation_source is not None:
            flags |= data.elevation_source.value << self.ELEVATION_SOURCE_SHIFT

        if data.heading_source is not None:
            flags |= data.heading_source.value << self.HEADING_SOURCE_SHIFT

        result.extend(DataParser.encode_int16(flags, signed=False))

        if data.instantaneous_speed is not None:
            speed_value = int(data.instantaneous_speed * 100)
            result.extend(DataParser.encode_int16(speed_value, signed=False))

        if data.total_distance is not None:
            distance_value = int(data.total_distance * 10)
            result.extend(DataParser.encode_int24(distance_value, signed=False))

        if data.latitude is not None and data.longitude is not None:
            lat_value = int(data.latitude * 10000000)
            lon_value = int(data.longitude * 10000000)
            result.extend(DataParser.encode_int32(lat_value, signed=True))
            result.extend(DataParser.encode_int32(lon_value, signed=True))

        if data.elevation is not None:
            elevation_value = int(data.elevation * 100)
            result.extend(DataParser.encode_int24(elevation_value, signed=True))

        if data.heading is not None:
            heading_value = int(data.heading * 100)
            result.extend(DataParser.encode_int16(heading_value, signed=False))

        if data.rolling_time is not None:
            result.append(data.rolling_time)

        if data.utc_time is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.utc_time))

        return result
