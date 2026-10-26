"""Channel Map Update Indication (AD 0x28, Core Spec Vol 3, Part C §11).

Decodes the Channel Map Update Indication AD type that carries a new
data-channel map and the connection-event instant at which it takes effect.
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.gatt.characteristics.utils import DataParser

# Channel Map Update Indication layout sizes
CHANNEL_MAP_LENGTH = 5  # 5-byte bitmask of data channels 0-36
CHANNEL_MAP_INSTANT_OFFSET = CHANNEL_MAP_LENGTH  # instant immediately follows map

# BLE data channel range (Core Spec Vol 6, Part B §1.4.1)
MAX_DATA_CHANNEL = 36


class ChannelMapUpdateIndication(msgspec.Struct, frozen=True, kw_only=True):
    """Channel Map Update Indication (Core Spec Vol 3, Part C, §11).

    Carries a new channel map and the connection-event instant at which
    it takes effect.

    Format: channel_map (5 bytes) + instant (2 bytes LE uint16).

    Attributes:
        channel_map: 5-byte bitmask of used data channels (channels 0-36).
            Bit *n* = 1 means channel *n* is in use.
        instant: Connection event count at which the new map takes effect.

    """

    channel_map: bytes
    instant: int

    @classmethod
    def decode(cls, data: bytes | bytearray) -> ChannelMapUpdateIndication:
        """Decode Channel Map Update Indication AD.

        DataParser raises ``InsufficientDataError`` if the payload is
        shorter than the required 7 bytes.

        Args:
            data: Raw AD data bytes (excluding length and AD type).

        Returns:
            Parsed ChannelMapUpdateIndication.

        """
        channel_map = bytes(data[:CHANNEL_MAP_LENGTH])
        instant = DataParser.parse_int16(data, CHANNEL_MAP_INSTANT_OFFSET, signed=False)

        return cls(channel_map=channel_map, instant=instant)

    def is_channel_used(self, channel: int) -> bool:
        """Check if a specific data channel is marked as used.

        Args:
            channel: Channel number (0-36).

        Returns:
            ``True`` if the channel is used in the new map.

        Raises:
            ValueError: If channel is out of range.

        """
        if not 0 <= channel <= MAX_DATA_CHANNEL:
            msg = f"Channel must be 0-{MAX_DATA_CHANNEL}, got {channel}"
            raise ValueError(msg)

        byte_index = channel // 8
        bit_index = channel % 8
        return bool(self.channel_map[byte_index] & (1 << bit_index))


__all__ = [
    "CHANNEL_MAP_LENGTH",
    "CHANNEL_MAP_INSTANT_OFFSET",
    "ChannelMapUpdateIndication",
    "MAX_DATA_CHANNEL",
]
