"""Step Counter Activity Summary Data characteristic (0x2B40).

Summary of step counter activity data with segmented header.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class StepCounterActivitySummaryFlags(IntFlag):
    """Step Counter Activity Summary Data flags (8-bit, 1 octet)."""

    NORMAL_WALKING_STEPS_PRESENT = 0x01
    INTENSITY_STEPS_PRESENT = 0x02
    FLOOR_STEPS_PRESENT = 0x04
    DISTANCE_PRESENT = 0x08
    WORN_DURATION_PRESENT = 0x10


class StepCounterActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Step Counter Activity Summary Data.

    Attributes:
        header: Segmentation header byte.
        flags: Presence flags for optional fields (8-bit).
        session_id: Session identifier (uint16).
        sub_session_id: Sub-session identifier (uint16).
        relative_timestamp: Relative timestamp in seconds (uint32).
        sequence_number: Sequence number (uint32).

    """

    header: int
    flags: StepCounterActivitySummaryFlags
    session_id: int
    sub_session_id: int
    relative_timestamp: int
    sequence_number: int


class StepCounterActivitySummaryDataCharacteristic(
    BaseCharacteristic[StepCounterActivitySummaryData],
):
    """Step Counter Activity Summary Data characteristic (0x2B40).

    org.bluetooth.characteristic.step_counter_activity_summary_data

    Summary of step counter activity with optional fields indicated
    by a flags field.
    """

    min_length = 14  # header(1) + flags(1) + session(2) + subsession(2) + timestamp(4) + sequence(4)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> StepCounterActivitySummaryData:
        """Parse Step Counter Activity Summary Data.

        Format: Header (uint8) + Flags (uint8) + SessionID (uint16)
                + SubSessionID (uint16) + RelativeTimestamp (uint32)
                + SequenceNumber (uint32) + [optional fields].
        """
        header = DataParser.parse_int8(data, 0, signed=False)
        flags = StepCounterActivitySummaryFlags(DataParser.parse_int8(data, 1, signed=False))
        session_id = DataParser.parse_int16(data, 2, signed=False)
        sub_session_id = DataParser.parse_int16(data, 4, signed=False)
        relative_timestamp = DataParser.parse_int32(data, 6, signed=False)
        sequence_number = DataParser.parse_int32(data, 10, signed=False)

        return StepCounterActivitySummaryData(
            header=header,
            flags=flags,
            session_id=session_id,
            sub_session_id=sub_session_id,
            relative_timestamp=relative_timestamp,
            sequence_number=sequence_number,
        )

    def _encode_value(self, data: StepCounterActivitySummaryData) -> bytearray:
        """Encode Step Counter Activity Summary Data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.header, signed=False))
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.session_id, signed=False))
        result.extend(DataParser.encode_int16(data.sub_session_id, signed=False))
        result.extend(DataParser.encode_int32(data.relative_timestamp, signed=False))
        result.extend(DataParser.encode_int32(data.sequence_number, signed=False))
        return result
