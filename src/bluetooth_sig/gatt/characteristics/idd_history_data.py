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
    """IDD history event types."""

    REFERENCE_TIME_BASE_CHANGED = 0x01
    BOLUS_PROGRAMMED = 0x02
    BOLUS_DELIVERED = 0x03
    BOLUS_CANCELLED = 0x04
    TBR_ACTIVATED = 0x05
    TBR_DEACTIVATED = 0x06
    PROFILE_TEMPLATE_ACTIVATED = 0x07
    BASAL_RATE_CHANGED = 0x08
    TOTAL_DAILY_INSULIN_CHANGED = 0x09
    THERAPY_CONTROL_STATE_CHANGED = 0x0A
    OPERATIONAL_STATE_CHANGED = 0x0B
    RESERVOIR_REMAINING_CHANGED = 0x0C
    ANNUNCIATION_STATUS_CHANGED = 0x0D
    MAX_BOLUS_AMOUNT_CHANGED = 0x0E


class IDDHistoryDataPayload(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD History Data characteristic.

    Attributes:
        sequence_number: Sequence number of this history event.
        event_type: Type of the history event.
        event_data: Raw event-specific data bytes.

    """

    sequence_number: int
    event_type: IDDHistoryEventType
    event_data: bytes = b""


class IDDHistoryDataCharacteristic(BaseCharacteristic[IDDHistoryDataPayload]):
    """IDD History Data characteristic (0x2B28).

    org.bluetooth.characteristic.idd_history_data

    Contains historical event data from the Insulin Delivery Device.
    """

    min_length = 3  # sequence_number(2) + event_type(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDHistoryDataPayload:
        """Parse IDD History Data.

        Format: SequenceNumber (uint16 LE) + EventType (uint8) + EventData (variable).
        """
        sequence_number = DataParser.parse_int16(data, 0, signed=False)
        event_type = IDDHistoryEventType(DataParser.parse_int8(data, 2, signed=False))
        event_data = bytes(data[3:])

        return IDDHistoryDataPayload(
            sequence_number=sequence_number,
            event_type=event_type,
            event_data=event_data,
        )

    def _encode_value(self, data: IDDHistoryDataPayload) -> bytearray:
        """Encode IDD History Data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.sequence_number, signed=False))
        result.extend(DataParser.encode_int8(int(data.event_type), signed=False))
        result.extend(data.event_data)
        return result
