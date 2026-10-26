"""Search Control Point characteristic (0x2BA7)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SearchControlPointType(IntEnum):
    """Search Control Point search types per MCS spec."""

    TRACK_NAME = 0x01
    ARTIST_NAME = 0x02
    ALBUM_NAME = 0x03
    GROUP_NAME = 0x04
    EARLIEST_YEAR = 0x05
    LATEST_YEAR = 0x06
    GENRE = 0x07
    ONLY_TRACKS = 0x08
    ONLY_GROUPS = 0x09


_PARAMETER_START_INDEX = 2


class SearchControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Search Control Point characteristic.

    Format: Length(uint8) + Type(uint8) + optional Parameter (UTF-8 string).
    """

    length: int
    search_type: SearchControlPointType
    parameter: str | None = None


class SearchControlPointCharacteristic(BaseCharacteristic[SearchControlPointData]):
    """Search Control Point characteristic (0x2BA7).

    org.bluetooth.characteristic.search_control_point

    Used for searching media in the Media Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SearchControlPointData:
        """Parse Search Control Point data.

        Format: length (uint8) + type (uint8) + optional parameter string.
        """
        length = DataParser.parse_int8(data, 0, signed=False)
        search_type = SearchControlPointType(DataParser.parse_int8(data, 1, signed=False))

        parameter = None
        if len(data) > _PARAMETER_START_INDEX:
            parameter = data[_PARAMETER_START_INDEX:].decode("utf-8", errors="replace")

        return SearchControlPointData(
            length=length,
            search_type=search_type,
            parameter=parameter,
        )

    def _encode_value(self, data: SearchControlPointData) -> bytearray:
        """Encode Search Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.length)
        result += DataParser.encode_int8(int(data.search_type))
        if data.parameter is not None:
            result += data.parameter.encode("utf-8")
        return result
