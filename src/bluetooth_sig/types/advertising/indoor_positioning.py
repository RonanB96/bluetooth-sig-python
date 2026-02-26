"""Indoor Positioning advertisement data (AD 0x25, CSS Part A §1.14).

Decodes the Indoor Positioning AD type whose configuration byte drives
which optional coordinate, power and altitude fields are present.
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.gatt.characteristics.utils import DataParser


class IndoorPositioningConfig(IntFlag):
    """Configuration byte flags for Indoor Positioning AD (CSS Part A §1.14).

    The configuration byte is the first octet of the AD data and determines
    which optional fields are present in the payload.
    """

    COORDINATE_SYSTEM_LOCAL = 0x01  # 0 = WGS84, 1 = local
    LATITUDE_PRESENT = 0x02
    LONGITUDE_PRESENT = 0x04
    LOCAL_NORTH_PRESENT = 0x08
    LOCAL_EAST_PRESENT = 0x10
    TX_POWER_PRESENT = 0x20
    FLOOR_NUMBER_PRESENT = 0x40
    ALTITUDE_PRESENT = 0x80


# Mask combining all location-bearing flag bits (used for uncertainty check)
LOCATION_FLAGS_MASK = (
    IndoorPositioningConfig.LATITUDE_PRESENT
    | IndoorPositioningConfig.LONGITUDE_PRESENT
    | IndoorPositioningConfig.LOCAL_NORTH_PRESENT
    | IndoorPositioningConfig.LOCAL_EAST_PRESENT
)


class IndoorPositioningData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed Indoor Positioning AD data (CSS Part A, §1.14).

    The configuration byte determines which optional fields are present.
    When ``is_local_coordinates`` is ``False``, WGS84 latitude/longitude
    fields are used; when ``True``, local north/east fields are used.

    Attributes:
        config: Raw configuration flags for reference.
        is_local_coordinates: ``True`` for local coordinate system, ``False`` for WGS84.
        latitude: WGS84 latitude in units of 1e-7 degrees (present when bit 1 set, WGS84 mode).
        longitude: WGS84 longitude in units of 1e-7 degrees (present when bit 2 set, WGS84 mode).
        local_north: Local north coordinate in 0.01 m units (present when bit 3 set, local mode).
        local_east: Local east coordinate in 0.01 m units (present when bit 4 set, local mode).
        tx_power: Transmit power level in dBm.
        floor_number: Floor number (offset by -20, so 0 means floor -20).
        altitude: Altitude in 0.01 m units (interpretation depends on coordinate system).
        uncertainty: Location uncertainty — bit 7 is stationary flag, bits 0-6 encode precision.

    """

    config: IndoorPositioningConfig = IndoorPositioningConfig(0)
    is_local_coordinates: bool = False
    latitude: int | None = None
    longitude: int | None = None
    local_north: int | None = None
    local_east: int | None = None
    tx_power: int | None = None
    floor_number: int | None = None
    altitude: int | None = None
    uncertainty: int | None = None

    @classmethod
    def decode(cls, data: bytes | bytearray) -> IndoorPositioningData:
        """Decode Indoor Positioning AD data.

        DataParser raises ``InsufficientDataError`` automatically if the
        payload is truncated mid-field.  Optional trailing fields use
        ``len(data) >= offset + N`` guards (same pattern as Heart Rate
        Measurement for optional fields).

        Args:
            data: Raw AD data bytes (excluding length and AD type).

        Returns:
            Parsed IndoorPositioningData.

        """
        config = IndoorPositioningConfig(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        is_local = bool(config & IndoorPositioningConfig.COORDINATE_SYSTEM_LOCAL)
        latitude: int | None = None
        longitude: int | None = None
        local_north: int | None = None
        local_east: int | None = None
        tx_power: int | None = None
        floor_number: int | None = None
        altitude: int | None = None
        uncertainty: int | None = None

        if not is_local:
            if config & IndoorPositioningConfig.LATITUDE_PRESENT:
                latitude = DataParser.parse_int32(data, offset, signed=True)
                offset += 4

            if config & IndoorPositioningConfig.LONGITUDE_PRESENT:
                longitude = DataParser.parse_int32(data, offset, signed=True)
                offset += 4
        else:
            if config & IndoorPositioningConfig.LOCAL_NORTH_PRESENT:
                local_north = DataParser.parse_int16(data, offset, signed=True)
                offset += 2

            if config & IndoorPositioningConfig.LOCAL_EAST_PRESENT:
                local_east = DataParser.parse_int16(data, offset, signed=True)
                offset += 2

        if config & IndoorPositioningConfig.TX_POWER_PRESENT:
            tx_power = DataParser.parse_int8(data, offset, signed=True)
            offset += 1

        if config & IndoorPositioningConfig.FLOOR_NUMBER_PRESENT:
            floor_number = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        if config & IndoorPositioningConfig.ALTITUDE_PRESENT:
            altitude = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Uncertainty is optional — present only when any location field exists
        if (config & LOCATION_FLAGS_MASK) and len(data) >= offset + 1:
            uncertainty = DataParser.parse_int8(data, offset, signed=False)

        return cls(
            config=config,
            is_local_coordinates=is_local,
            latitude=latitude,
            longitude=longitude,
            local_north=local_north,
            local_east=local_east,
            tx_power=tx_power,
            floor_number=floor_number,
            altitude=altitude,
            uncertainty=uncertainty,
        )


__all__ = [
    "IndoorPositioningConfig",
    "IndoorPositioningData",
    "LOCATION_FLAGS_MASK",
]
