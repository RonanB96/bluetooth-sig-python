"""Broadcast Receive State characteristic (0x2BC8)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class PASyncState(IntEnum):
    """PA Sync State values."""

    NOT_SYNCHRONIZED = 0x00
    SYNC_INFO_REQUEST = 0x01
    SYNCHRONIZED = 0x02
    FAILED_TO_SYNCHRONIZE = 0x03
    NO_PAST = 0x04


class BIGEncryption(IntEnum):
    """BIG Encryption state values."""

    NOT_ENCRYPTED = 0x00
    BROADCAST_CODE_REQUIRED = 0x01
    DECRYPTING = 0x02
    BAD_CODE = 0x03


class BroadcastReceiveStateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Broadcast Receive State characteristic.

    Contains the source identification, sync state, encryption state,
    and any additional subgroup data as raw bytes.
    """

    source_id: int
    source_address_type: int
    source_address: bytes
    source_adv_sid: int
    broadcast_id: int
    pa_sync_state: PASyncState
    big_encryption: BIGEncryption
    additional_data: bytes = b""


class BroadcastReceiveStateCharacteristic(BaseCharacteristic[BroadcastReceiveStateData]):
    """Broadcast Receive State characteristic (0x2BC8).

    org.bluetooth.characteristic.broadcast_receive_state

    Contains state information about a broadcast audio source
    being received.
    """

    # Minimum 13 bytes for mandatory fields, but allow variable length for optional data
    min_length = 13
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BroadcastReceiveStateData:
        """Parse Broadcast Receive State data.

        Format: Source_ID(uint8) + Source_Address_Type(uint8) + Source_Address(6 bytes)
        + Source_Adv_SID(uint8) + Broadcast_ID(uint24) + PA_Sync_State(uint8)
        + BIG_Encryption(uint8) + optional additional data.
        """
        offset = 0
        source_id = DataParser.parse_int8(data, offset, signed=False)
        offset += 1
        source_address_type = DataParser.parse_int8(data, offset, signed=False)
        offset += 1
        source_address = bytes(data[offset : offset + 6])
        offset += 6
        source_adv_sid = DataParser.parse_int8(data, offset, signed=False)
        offset += 1
        broadcast_id = DataParser.parse_int24(data, offset, signed=False)
        offset += 3
        pa_sync_state = PASyncState(DataParser.parse_int8(data, offset, signed=False))
        offset += 1
        big_encryption = BIGEncryption(DataParser.parse_int8(data, offset, signed=False))
        offset += 1
        additional_data = bytes(data[offset:]) if offset < len(data) else b""

        return BroadcastReceiveStateData(
            source_id=source_id,
            source_address_type=source_address_type,
            source_address=source_address,
            source_adv_sid=source_adv_sid,
            broadcast_id=broadcast_id,
            pa_sync_state=pa_sync_state,
            big_encryption=big_encryption,
            additional_data=additional_data,
        )

    def _encode_value(self, data: BroadcastReceiveStateData) -> bytearray:
        """Encode Broadcast Receive State data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.source_id)
        result += DataParser.encode_int8(data.source_address_type)
        result += bytearray(data.source_address)
        result += DataParser.encode_int8(data.source_adv_sid)
        result += DataParser.encode_int24(data.broadcast_id, signed=False)
        result += DataParser.encode_int8(int(data.pa_sync_state))
        result += DataParser.encode_int8(int(data.big_encryption))
        result += bytearray(data.additional_data)
        return result
