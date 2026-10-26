"""Source ASE characteristic (0x2BC5)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SourceASEState(IntEnum):
    """Audio Stream Endpoint state values."""

    IDLE = 0x00
    CODEC_CONFIGURED = 0x01
    QOS_CONFIGURED = 0x02
    ENABLING = 0x03
    STREAMING = 0x04
    DISABLING = 0x05
    RELEASING = 0x06


_ADDITIONAL_DATA_START_INDEX = 2


class SourceASEData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Source ASE characteristic.

    Contains the ASE ID, current state, and any additional
    state-specific data as raw bytes.
    """

    ase_id: int
    ase_state: SourceASEState
    additional_data: bytes = b""


class SourceASECharacteristic(BaseCharacteristic[SourceASEData]):
    """Source ASE characteristic (0x2BC5).

    org.bluetooth.characteristic.source_ase

    Audio Stream Endpoint for source (audio transmitter) role.
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SourceASEData:
        """Parse Source ASE data.

        Format: ASE_ID (uint8) + ASE_State (uint8) + variable state-specific data.
        """
        ase_id = DataParser.parse_int8(data, 0, signed=False)
        ase_state = SourceASEState(DataParser.parse_int8(data, 1, signed=False))
        additional_data = (
            bytes(data[_ADDITIONAL_DATA_START_INDEX:]) if len(data) > _ADDITIONAL_DATA_START_INDEX else b""
        )

        return SourceASEData(
            ase_id=ase_id,
            ase_state=ase_state,
            additional_data=additional_data,
        )

    def _encode_value(self, data: SourceASEData) -> bytearray:
        """Encode Source ASE data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.ase_id)
        result += DataParser.encode_int8(int(data.ase_state))
        result += bytearray(data.additional_data)
        return result
