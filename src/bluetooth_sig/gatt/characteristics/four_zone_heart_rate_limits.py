"""Four Zone Heart Rate Limits characteristic (0x2B4C)."""

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class FourZoneHeartRateLimitsData(msgspec.Struct, frozen=True, kw_only=True):
    """Four Zone Heart Rate Limits data structure."""

    light_moderate_limit: int
    moderate_hard_limit: int
    hard_maximum_limit: int


class FourZoneHeartRateLimitsCharacteristic(BaseCharacteristic):
    """Four Zone Heart Rate Limits characteristic (0x2B4C).

    org.bluetooth.characteristic.four_zone_heart_rate_limits

    The Four Zone Heart Rate Limits characteristic is used to represent the limits
    between the heart rate zones for the four-zone heart rate definition
    (Maximum, Hard, Moderate, and Light) of a user.
    """

    expected_length = 3

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> FourZoneHeartRateLimitsData:
        """Decode Four Zone Heart Rate Limits from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (3 bytes)
            ctx: Optional context for parsing

        Returns:
            FourZoneHeartRateLimitsData: Parsed heart rate limits
        """
        light_moderate_limit = DataParser.parse_int8(data, 0, signed=False)
        moderate_hard_limit = DataParser.parse_int8(data, 1, signed=False)
        hard_maximum_limit = DataParser.parse_int8(data, 2, signed=False)

        return FourZoneHeartRateLimitsData(
            light_moderate_limit=light_moderate_limit,
            moderate_hard_limit=moderate_hard_limit,
            hard_maximum_limit=hard_maximum_limit,
        )

    def encode_value(self, data: FourZoneHeartRateLimitsData) -> bytearray:
        """Encode Four Zone Heart Rate Limits to raw bytes.

        Args:
            data: FourZoneHeartRateLimitsData to encode

        Returns:
            bytearray: Encoded bytes
        """
        result = bytearray()
        result.extend(DataParser.encode_int8(data.light_moderate_limit, signed=False))
        result.extend(DataParser.encode_int8(data.moderate_hard_limit, signed=False))
        result.extend(DataParser.encode_int8(data.hard_maximum_limit, signed=False))
        return result
