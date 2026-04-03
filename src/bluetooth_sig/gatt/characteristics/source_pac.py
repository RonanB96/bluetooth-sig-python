"""Source PAC characteristic (0x2BCB)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SourcePACData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Source PAC characteristic.

    Contains the number of PAC records and the raw record data.
    Full PAC record parsing is complex (codec_id + capabilities + metadata)
    and stored as raw bytes for downstream consumers.
    """

    number_of_pac_records: int
    raw_data: bytes


class SourcePACCharacteristic(BaseCharacteristic[SourcePACData]):
    """Source PAC characteristic (0x2BCB).

    org.bluetooth.characteristic.source_pac

    Published Audio Capabilities for the source role.
    Contains codec capabilities for audio transmission.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SourcePACData:
        """Parse Source PAC data.

        Format: number_of_pac_records (uint8) + variable PAC records.
        """
        record_count = DataParser.parse_int8(data, 0, signed=False)
        raw_data = bytes(data[1:]) if len(data) > 1 else b""
        return SourcePACData(
            number_of_pac_records=record_count,
            raw_data=raw_data,
        )

    def _encode_value(self, data: SourcePACData) -> bytearray:
        """Encode Source PAC data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(data.number_of_pac_records)
        result += bytearray(data.raw_data)
        return result
