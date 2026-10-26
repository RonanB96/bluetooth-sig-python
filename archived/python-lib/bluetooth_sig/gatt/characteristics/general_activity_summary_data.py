"""General Activity Summary Data characteristic (0x2B3D).

Reports summary statistics for a general activity period.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GeneralActivitySummaryFlags(IntFlag):
    """General Activity Summary Data flags (32-bit, 4 octets)."""

    NORMAL_WALKING_EE_PRESENT = 0x00000001
    INTENSITY_EE_PRESENT = 0x00000002
    TOTAL_EE_PRESENT = 0x00000004
    FAT_BURNED_PRESENT = 0x00000008
    MIN_METABOLIC_EQUIVALENT_PRESENT = 0x00000010
    MAX_METABOLIC_EQUIVALENT_PRESENT = 0x00000020
    AVG_METABOLIC_EQUIVALENT_PRESENT = 0x00000040
    DISTANCE_PRESENT = 0x00000080
    MIN_SPEED_PRESENT = 0x00000100
    MAX_SPEED_PRESENT = 0x00000200
    AVG_SPEED_PRESENT = 0x00000400
    DURATION_NORMAL_WALKING_PRESENT = 0x00000800
    DURATION_INTENSITY_WALKING_PRESENT = 0x00001000
    MIN_MOTION_CADENCE_PRESENT = 0x00002000
    MAX_MOTION_CADENCE_PRESENT = 0x00004000
    AVG_MOTION_CADENCE_PRESENT = 0x00008000
    FLOORS_PRESENT = 0x00010000
    POSITIVE_ELEVATION_GAIN_PRESENT = 0x00020000
    NEGATIVE_ELEVATION_GAIN_PRESENT = 0x00040000
    ACTIVITY_COUNT_PRESENT = 0x00080000
    MIN_ACTIVITY_LEVEL_PRESENT = 0x00100000
    MAX_ACTIVITY_LEVEL_PRESENT = 0x00200000
    AVG_ACTIVITY_LEVEL_PRESENT = 0x00400000
    AVG_ACTIVITY_TYPE_PRESENT = 0x00800000
    WORN_DURATION_PRESENT = 0x01000000


class GeneralActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from General Activity Summary Data characteristic.

    Attributes:
        header: Segmentation header byte.
        flags: Presence flags for optional fields (32-bit).
        session_id: Session identifier (uint16).
        sub_session_id: Sub-session identifier (uint16).
        relative_timestamp: Relative timestamp in seconds (uint32).
        sequence_number: Sequence number (uint32).

    """

    header: int
    flags: GeneralActivitySummaryFlags
    session_id: int
    sub_session_id: int
    relative_timestamp: int
    sequence_number: int


class GeneralActivitySummaryDataCharacteristic(BaseCharacteristic[GeneralActivitySummaryData]):
    """General Activity Summary Data characteristic (0x2B3D).

    org.bluetooth.characteristic.general_activity_summary_data

    Reports summary statistics for a general activity period.
    """

    min_length = 17  # header(1) + flags(4) + session(2) + subsession(2) + timestamp(4) + sequence(4)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GeneralActivitySummaryData:
        """Parse General Activity Summary Data.

        Format: Header (uint8) + Flags (uint32) + SessionID (uint16)
                + SubSessionID (uint16) + RelativeTimestamp (uint32)
                + SequenceNumber (uint32) + [optional fields].
        """
        header = DataParser.parse_int8(data, 0, signed=False)
        flags_raw = DataParser.parse_int32(data, 1, signed=False)
        flags = GeneralActivitySummaryFlags(flags_raw)
        session_id = DataParser.parse_int16(data, 5, signed=False)
        sub_session_id = DataParser.parse_int16(data, 7, signed=False)
        relative_timestamp = DataParser.parse_int32(data, 9, signed=False)
        sequence_number = DataParser.parse_int32(data, 13, signed=False)

        return GeneralActivitySummaryData(
            header=header,
            flags=flags,
            session_id=session_id,
            sub_session_id=sub_session_id,
            relative_timestamp=relative_timestamp,
            sequence_number=sequence_number,
        )

    def _encode_value(self, data: GeneralActivitySummaryData) -> bytearray:
        """Encode General Activity Summary data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.header, signed=False))
        result.extend(DataParser.encode_int32(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.session_id, signed=False))
        result.extend(DataParser.encode_int16(data.sub_session_id, signed=False))
        result.extend(DataParser.encode_int32(data.relative_timestamp, signed=False))
        result.extend(DataParser.encode_int32(data.sequence_number, signed=False))
        return result
