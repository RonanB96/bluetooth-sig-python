"""Cooking Sensor Info Descriptor implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

from ..characteristics.utils import DataParser
from ..constants import SIZE_UINT8, SIZE_UINT16, SIZE_UUID16
from .base import BaseDescriptor

_AGGREGATE_OFFSET_SIZE = SIZE_UINT16
_SENSOR_INFO_MIN_LENGTH = SIZE_UUID16 + SIZE_UINT8 + SIZE_UINT8 + SIZE_UINT8


class CookingSensorLocationType(IntEnum):
    """Permitted Cooking Sensor Info location types from CWS Table 3.20."""

    VESSEL_SIDE = 0x01
    VESSEL_BOTTOM = 0x02
    GRILL_PLATE = 0x03
    LID = 0x04
    PROBE_FOOD_CORE = 0x05
    PROBE_AMBIENT = 0x06
    HANDLE = 0x07
    ELECTRONICS_BATTERY = 0x08
    OTHER_UNKNOWN = 0xFF


class CookingSensorLocation(msgspec.Struct, frozen=True, kw_only=True):
    """Typed Sensor Location field from the Cooking Sensor Info descriptor."""

    location_type: CookingSensorLocationType
    distance_mm: int | None = None


class CookingSensorInfoData(msgspec.Struct, frozen=True, kw_only=True):
    """Cooking Sensor Info descriptor data."""

    sensor_uuid: BluetoothUUID
    measurement_uncertainty: int
    location: CookingSensorLocation
    aggregate_offset: int | None = None


class CookingSensorInfoDescriptor(BaseDescriptor):
    """Cooking Sensor Info Descriptor (0x2916)."""

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> CookingSensorInfoData:
        if len(data) < _SENSOR_INFO_MIN_LENGTH:
            raise ValueError(
                f"Cooking Sensor Info descriptor needs at least {_SENSOR_INFO_MIN_LENGTH} bytes, got {len(data)}"
            )

        sensor_uuid = BluetoothUUID(DataParser.parse_int16(data, 0, signed=False, endian="little"))
        measurement_uncertainty = DataParser.parse_int8(data, SIZE_UUID16, signed=False)
        location_type = DataParser.parse_int8(data, SIZE_UUID16 + SIZE_UINT8, signed=False)
        location_data_size = DataParser.parse_int8(data, SIZE_UUID16 + SIZE_UINT8 + SIZE_UINT8, signed=False)

        location_data_start = _SENSOR_INFO_MIN_LENGTH
        location_data_end = location_data_start + location_data_size
        if len(data) < location_data_end:
            raise ValueError(
                "Cooking Sensor Info descriptor location data is shorter than the declared Location Data Size"
            )
        location = _parse_location(location_type, data[location_data_start:location_data_end])

        remaining = len(data) - location_data_end
        if remaining not in {0, _AGGREGATE_OFFSET_SIZE}:
            raise ValueError("Cooking Sensor Info descriptor has invalid trailing aggregate offset length")

        aggregate_offset = None
        if remaining == _AGGREGATE_OFFSET_SIZE:
            aggregate_offset = DataParser.parse_int16(data, location_data_end, signed=False, endian="little")

        return CookingSensorInfoData(
            sensor_uuid=sensor_uuid,
            measurement_uncertainty=measurement_uncertainty,
            location=location,
            aggregate_offset=aggregate_offset,
        )


def _parse_location(location_type_raw: int, location_data: bytes) -> CookingSensorLocation:
    """Parse the typed Sensor Location field from CWS Table 3.20."""
    try:
        location_type = CookingSensorLocationType(location_type_raw)
    except ValueError as exc:
        raise ValueError("Cooking Sensor Info location type is RFU") from exc

    if location_type in {
        CookingSensorLocationType.VESSEL_SIDE,
        CookingSensorLocationType.VESSEL_BOTTOM,
        CookingSensorLocationType.GRILL_PLATE,
        CookingSensorLocationType.LID,
        CookingSensorLocationType.PROBE_FOOD_CORE,
        CookingSensorLocationType.PROBE_AMBIENT,
    }:
        if len(location_data) != SIZE_UINT16:
            raise ValueError("Cooking Sensor Info location type requires 2 bytes of location data")
        return CookingSensorLocation(
            location_type=location_type,
            distance_mm=DataParser.parse_int16(location_data, 0, signed=False, endian="little"),
        )

    if len(location_data) != 0:
        raise ValueError("Cooking Sensor Info location type does not include location data")
    return CookingSensorLocation(location_type=location_type)
