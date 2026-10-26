"""Five Zone Heart Rate Limits characteristic (0x2A8B)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class FiveZoneHeartRateLimitsData(msgspec.Struct, frozen=True, kw_only=True):
    """Five Zone Heart Rate Limits data structure."""

    very_light_light_limit: int
    light_moderate_limit: int
    moderate_hard_limit: int
    hard_maximum_limit: int


class FiveZoneHeartRateLimitsCharacteristic(BaseCharacteristic[FiveZoneHeartRateLimitsData]):
    """Five Zone Heart Rate Limits characteristic (0x2A8B).

    org.bluetooth.characteristic.five_zone_heart_rate_limits

    The Five Zone Heart Rate Limits characteristic is used to represent the limits
    between the heart rate zones for the five-zone heart rate definition
    (Maximum, Hard, Moderate, Light, and Very Light) of a user.
    """

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> FiveZoneHeartRateLimitsData:
        """Decode Five Zone Heart Rate Limits from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (4 bytes)
            ctx: Optional context for parsing
            validate: Whether to validate ranges (default True)

        Returns:
            FiveZoneHeartRateLimitsData: Parsed heart rate limits
        """
        very_light_light_limit = DataParser.parse_int8(data, 0, signed=False)
        light_moderate_limit = DataParser.parse_int8(data, 1, signed=False)
        moderate_hard_limit = DataParser.parse_int8(data, 2, signed=False)
        hard_maximum_limit = DataParser.parse_int8(data, 3, signed=False)

        return FiveZoneHeartRateLimitsData(
            very_light_light_limit=very_light_light_limit,
            light_moderate_limit=light_moderate_limit,
            moderate_hard_limit=moderate_hard_limit,
            hard_maximum_limit=hard_maximum_limit,
        )

    def _encode_value(self, data: FiveZoneHeartRateLimitsData) -> bytearray:
        """Encode Five Zone Heart Rate Limits to raw bytes.

        Args:
            data: FiveZoneHeartRateLimitsData to encode

        Returns:
            bytearray: Encoded bytes
        """
        result = bytearray()
        result.extend(DataParser.encode_int8(data.very_light_light_limit, signed=False))
        result.extend(DataParser.encode_int8(data.light_moderate_limit, signed=False))
        result.extend(DataParser.encode_int8(data.moderate_hard_limit, signed=False))
        result.extend(DataParser.encode_int8(data.hard_maximum_limit, signed=False))
        return result
