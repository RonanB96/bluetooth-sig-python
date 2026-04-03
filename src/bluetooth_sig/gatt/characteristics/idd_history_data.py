"""IDD History Data characteristic (0x2B28).

Contains historical event data from the Insulin Delivery Device.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDHistoryEventType(IntEnum):
    """IDD history event types (Table 4.95, Hamming codes)."""

    REFERENCE_TIME = 0x000F
    REFERENCE_TIME_BASE_OFFSET = 0x0033
    BOLUS_CALCULATED_PART_1 = 0x003C
    BOLUS_CALCULATED_PART_2 = 0x0055
    BOLUS_PROGRAMMED_PART_1 = 0x005A
    BOLUS_PROGRAMMED_PART_2 = 0x0066
    BOLUS_DELIVERED_PART_1 = 0x0069
    BOLUS_DELIVERED_PART_2 = 0x0096
    DELIVERED_BASAL_RATE_CHANGED = 0x0099
    TBR_ADJUSTMENT_STARTED = 0x00A5
    TBR_ADJUSTMENT_ENDED = 0x00AA
    TBR_ADJUSTMENT_CHANGED = 0x00C3
    PROFILE_TEMPLATE_ACTIVATED = 0x00CC
    BASAL_RATE_PROFILE_TEMPLATE_TIME_BLOCK_CHANGED = 0x00F0
    TOTAL_DAILY_INSULIN_DELIVERY = 0x00FF
    THERAPY_CONTROL_STATE_CHANGED = 0x0303
    OPERATIONAL_STATE_CHANGED = 0x030C
    RESERVOIR_REMAINING_AMOUNT_CHANGED = 0x0330
    ANNUNCIATION_STATUS_CHANGED_PART_1 = 0x033F
    ANNUNCIATION_STATUS_CHANGED_PART_2 = 0x0356
    ISF_PROFILE_TEMPLATE_TIME_BLOCK_CHANGED = 0x0359
    I2CHO_RATIO_PROFILE_TEMPLATE_TIME_BLOCK_CHANGED = 0x0365
    TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE_TIME_BLOCK_CHANGED = 0x036A
    PRIMING_STARTED = 0x0395
    PRIMING_DONE = 0x039A
    DATA_CORRUPTION = 0x03A6
    POINTER_EVENT = 0x03A9
    BOLUS_TEMPLATE_CHANGED_PART_1 = 0x03C0
    BOLUS_TEMPLATE_CHANGED_PART_2 = 0x03CF
    TBR_TEMPLATE_CHANGED = 0x03F3
    MAX_BOLUS_AMOUNT_CHANGED = 0x03FC
    MANUFACTURER_RESERVED_START = 0xF000
    MANUFACTURER_RESERVED_END = 0xFFF0


class IDDHistoryDataPayload(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD History Data characteristic.

    Attributes:
        event_type: Type of the history event (uint16).
        sequence_number: Sequence number of this history event (uint32).
        relative_offset: Relative time offset in seconds (uint16).
        event_data: Raw event-specific data bytes.

    """

    event_type: IDDHistoryEventType
    sequence_number: int
    relative_offset: int
    event_data: bytes = b""


class IDDHistoryDataCharacteristic(BaseCharacteristic[IDDHistoryDataPayload]):
    """IDD History Data characteristic (0x2B28).

    org.bluetooth.characteristic.idd_history_data

    Contains historical event data from the Insulin Delivery Device.
    """

    min_length = 8  # event_type(2) + sequence_number(4) + relative_offset(2)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDHistoryDataPayload:
        """Parse IDD History Data.

        Format: EventType (uint16 LE) + SequenceNumber (uint32 LE) + RelativeOffset (uint16 LE) + EventData (variable).
        """
        event_type = IDDHistoryEventType(DataParser.parse_int16(data, 0, signed=False))
        sequence_number = DataParser.parse_int32(data, 2, signed=False)
        relative_offset = DataParser.parse_int16(data, 6, signed=False)
        event_data = bytes(data[8:])

        return IDDHistoryDataPayload(
            event_type=event_type,
            sequence_number=sequence_number,
            relative_offset=relative_offset,
            event_data=event_data,
        )

    def _encode_value(self, data: IDDHistoryDataPayload) -> bytearray:
        """Encode IDD History Data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.event_type), signed=False))
        result.extend(DataParser.encode_int32(data.sequence_number, signed=False))
        result.extend(DataParser.encode_int16(data.relative_offset, signed=False))
        result.extend(data.event_data)
        return result
