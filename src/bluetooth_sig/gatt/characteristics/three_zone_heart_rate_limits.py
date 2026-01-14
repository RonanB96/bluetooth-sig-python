"""Three Zone Heart Rate Limits characteristic (0x2A94)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class ThreeZoneHeartRateLimitsData(msgspec.Struct, frozen=True, kw_only=True):
    """Three Zone Heart Rate Limits data structure."""

    light_moderate_limit: int
    moderate_hard_limit: int


class ThreeZoneHeartRateLimitsCharacteristic(BaseCharacteristic[ThreeZoneHeartRateLimitsData]):
    """Three Zone Heart Rate Limits characteristic (0x2A94).

    org.bluetooth.characteristic.three_zone_heart_rate_limits

    The Three Zone Heart Rate Limits characteristic is used to represent the limits
    between the heart rate zones for the three-zone heart rate definition
    (Hard, Moderate, and Light) of a user.
    """

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> ThreeZoneHeartRateLimitsData:
        """Decode Three Zone Heart Rate Limits from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (2 bytes)
            ctx: Optional context for parsing

        Returns:
            ThreeZoneHeartRateLimitsData: Parsed heart rate limits
        """
        light_moderate_limit = DataParser.parse_int8(data, 0, signed=False)
        moderate_hard_limit = DataParser.parse_int8(data, 1, signed=False)

        return ThreeZoneHeartRateLimitsData(
            light_moderate_limit=light_moderate_limit,
            moderate_hard_limit=moderate_hard_limit,
        )

    def _encode_value(self, data: ThreeZoneHeartRateLimitsData) -> bytearray:
        """Encode Three Zone Heart Rate Limits to raw bytes.

        Args:
            data: ThreeZoneHeartRateLimitsData to encode

        Returns:
            bytearray: Encoded bytes
        """
        result = bytearray()
        result.extend(DataParser.encode_int8(data.light_moderate_limit, signed=False))
        result.extend(DataParser.encode_int8(data.moderate_hard_limit, signed=False))
        return result
