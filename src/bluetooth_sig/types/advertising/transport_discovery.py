"""Transport Discovery Data (AD 0x26, CSS Part A §1.10).

Decodes the Transport Discovery Data AD type which carries one or more
transport blocks describing available transport connections.
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.gatt.characteristics.utils import DataParser

# Transport block header: org_id (1) + flags (1) + data_length (1)
TRANSPORT_BLOCK_HEADER_LENGTH = 3


class TDSFlags(IntFlag):
    """Transport Discovery Service flags (CSS Part A §1.10).

    Encoded in a single byte per transport block.
    """

    ROLE_NOT_SPECIFIED = 0x00
    ROLE_SEEKER = 0x01
    ROLE_PROVIDER = 0x02
    ROLE_SEEKER_AND_PROVIDER = 0x03
    INCOMPLETE = 0x04        # Bit 2: transport data is incomplete
    STATE_OFF = 0x00         # Bits 3-4 = 0b00
    STATE_ON = 0x08          # Bits 3-4 = 0b01
    STATE_TEMPORARILY_UNAVAILABLE = 0x10  # Bits 3-4 = 0b10


# Masks for extracting sub-fields from TDSFlags
TDS_ROLE_MASK = TDSFlags.ROLE_SEEKER | TDSFlags.ROLE_PROVIDER
TDS_STATE_MASK = TDSFlags.STATE_ON | TDSFlags.STATE_TEMPORARILY_UNAVAILABLE


class TransportBlock(msgspec.Struct, frozen=True, kw_only=True):
    """A single transport block within Transport Discovery Data.

    Attributes:
        organization_id: Organisation defining the transport data (1 = Bluetooth SIG).
        flags: TDS flags — role, incomplete, and transport state.
        transport_data: Organisation-specific transport payload.

    """

    organization_id: int
    flags: TDSFlags
    transport_data: bytes = b""

    @property
    def role(self) -> TDSFlags:
        """Role bits (0-1): seeker, provider, both, or not specified."""
        return self.flags & TDS_ROLE_MASK

    @property
    def is_incomplete(self) -> bool:
        """Whether transport data is incomplete (bit 2)."""
        return bool(self.flags & TDSFlags.INCOMPLETE)

    @property
    def transport_state(self) -> TDSFlags:
        """Transport state (bits 3-4): off, on, or temporarily unavailable."""
        return self.flags & TDS_STATE_MASK


class TransportDiscoveryData(msgspec.Struct, frozen=True, kw_only=True):
    """Transport Discovery Data (CSS Part A, §1.10).

    Contains one or more transport blocks describing available transport
    connections (e.g. Wi-Fi, classic Bluetooth).

    Attributes:
        blocks: List of parsed transport blocks.

    """

    blocks: list[TransportBlock] = msgspec.field(default_factory=list)

    @classmethod
    def decode(cls, data: bytes | bytearray) -> TransportDiscoveryData:
        """Decode Transport Discovery Data AD.

        Iterates over transport blocks until the buffer is exhausted.
        DataParser raises ``InsufficientDataError`` if a block header is
        truncated.  Incomplete trailing blocks (fewer than
        ``TRANSPORT_BLOCK_HEADER_LENGTH`` bytes remaining) are silently
        skipped, matching real-world scanner behaviour.

        Args:
            data: Raw AD data bytes (excluding length and AD type).

        Returns:
            Parsed TransportDiscoveryData with transport blocks.

        """
        blocks: list[TransportBlock] = []
        offset = 0

        while offset + TRANSPORT_BLOCK_HEADER_LENGTH <= len(data):
            org_id = DataParser.parse_int8(data, offset, signed=False)
            tds_flags = TDSFlags(DataParser.parse_int8(data, offset + 1, signed=False))
            transport_data_length = DataParser.parse_int8(data, offset + 2, signed=False)
            offset += TRANSPORT_BLOCK_HEADER_LENGTH

            end = min(offset + transport_data_length, len(data))
            transport_data = bytes(data[offset:end])
            offset = end

            blocks.append(TransportBlock(
                organization_id=org_id,
                flags=tds_flags,
                transport_data=transport_data,
            ))

        return cls(blocks=blocks)


__all__ = [
    "TDSFlags",
    "TDS_ROLE_MASK",
    "TDS_STATE_MASK",
    "TRANSPORT_BLOCK_HEADER_LENGTH",
    "TransportBlock",
    "TransportDiscoveryData",
]
