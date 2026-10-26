"""ACS Status characteristic (0x2B2F)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ACSStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ACS Status characteristic."""

    security_controls_switch: bool
    security_established: bool
    current_restriction_map_id: int


class ACSStatusCharacteristic(BaseCharacteristic[ACSStatusData]):
    """ACS Status characteristic (0x2B2F).

    org.bluetooth.characteristic.acs_status

    Contains ACS status flags and the current restriction map ID.
    """

    expected_length: int | None = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ACSStatusData:
        status_flags = DataParser.parse_int8(data, 0, signed=False)
        restriction_map_id = DataParser.parse_int16(data, 1, signed=False)

        return ACSStatusData(
            security_controls_switch=bool(status_flags & 0x01),
            security_established=bool(status_flags & 0x02),
            current_restriction_map_id=restriction_map_id,
        )

    def _encode_value(self, data: ACSStatusData) -> bytearray:
        status_flags = 0
        if data.security_controls_switch:
            status_flags |= 0x01
        if data.security_established:
            status_flags |= 0x02

        result = bytearray()
        result.extend(DataParser.encode_int8(status_flags, signed=False))
        result.extend(DataParser.encode_int16(data.current_restriction_map_id, signed=False))
        return result
