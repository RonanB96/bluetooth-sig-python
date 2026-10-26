"""General Activity Instantaneous Data characteristic (0x2B3C).

Reports instantaneous general activity data with segmented header.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GeneralActivityInstFlags(IntFlag):
    """General Activity Instantaneous Data flags (24-bit, 3 octets)."""

    NORMAL_WALKING_EE_PER_HOUR_PRESENT = 0x000001
    INTENSITY_EE_PER_HOUR_PRESENT = 0x000002
    TOTAL_EE_PER_HOUR_PRESENT = 0x000004
    FAT_BURNED_PER_HOUR_PRESENT = 0x000008
    METABOLIC_EQUIVALENT_PRESENT = 0x000010
    SPEED_PRESENT = 0x000020
    MOTION_CADENCE_PRESENT = 0x000040
    ELEVATION_PRESENT = 0x000080
    ACTIVITY_COUNT_PER_MINUTE_PRESENT = 0x000100
    ACTIVITY_LEVEL_PRESENT = 0x000200
    ACTIVITY_TYPE_PRESENT = 0x000400
    DEVICE_WORN = 0x800000


class GeneralActivityInstantaneousData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from General Activity Instantaneous Data characteristic.

    Attributes:
        header: Segmentation header byte.
        flags: Presence flags for optional fields (24-bit).
        session_id: Session identifier (uint16).
        sub_session_id: Sub-session identifier (uint16).
        relative_timestamp: Relative timestamp in seconds (uint32).
        sequence_number: Sequence number (uint32).

    """

    header: int
    flags: GeneralActivityInstFlags
    session_id: int
    sub_session_id: int
    relative_timestamp: int
    sequence_number: int


class GeneralActivityInstantaneousDataCharacteristic(BaseCharacteristic[GeneralActivityInstantaneousData]):
    """General Activity Instantaneous Data characteristic (0x2B3C).

    org.bluetooth.characteristic.general_activity_instantaneous_data

    Reports instantaneous general activity data.
    """

    min_length = 16  # header(1) + flags(3) + session(2) + subsession(2) + timestamp(4) + sequence(4)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GeneralActivityInstantaneousData:
        """Parse General Activity Instantaneous Data.

        Format: Header (uint8) + Flags (uint24) + SessionID (uint16)
                + SubSessionID (uint16) + RelativeTimestamp (uint32)
                + SequenceNumber (uint32) + [optional fields].
        """
        header = DataParser.parse_int8(data, 0, signed=False)
        flags_raw = DataParser.parse_int24(data, 1, signed=False)
        flags = GeneralActivityInstFlags(flags_raw)
        session_id = DataParser.parse_int16(data, 4, signed=False)
        sub_session_id = DataParser.parse_int16(data, 6, signed=False)
        relative_timestamp = DataParser.parse_int32(data, 8, signed=False)
        sequence_number = DataParser.parse_int32(data, 12, signed=False)

        return GeneralActivityInstantaneousData(
            header=header,
            flags=flags,
            session_id=session_id,
            sub_session_id=sub_session_id,
            relative_timestamp=relative_timestamp,
            sequence_number=sequence_number,
        )

    def _encode_value(self, data: GeneralActivityInstantaneousData) -> bytearray:
        """Encode General Activity Instantaneous data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.header, signed=False))
        result.extend(DataParser.encode_int24(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.session_id, signed=False))
        result.extend(DataParser.encode_int16(data.sub_session_id, signed=False))
        result.extend(DataParser.encode_int32(data.relative_timestamp, signed=False))
        result.extend(DataParser.encode_int32(data.sequence_number, signed=False))
        return result
