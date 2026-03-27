"""Physical Activity Session Descriptor characteristic (0x2B45).

Describes properties of a completed or ongoing activity session.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class PAMSessionStatus(IntEnum):
    """Physical Activity session status."""

    COMPLETE = 0x00
    IN_PROGRESS = 0x01
    PAUSED = 0x02


class ActivityType(IntEnum):
    """Physical Activity session activity type (PAMS v1.0 Table 3.7)."""

    UNSPECIFIED = 0x00
    OTHER = 0x01
    SIT = 0x02
    LIE = 0x03
    STAND = 0x04
    WALK = 0x05
    SHUFFLE = 0x06
    RUN = 0x07
    CYCLE_INDOOR = 0x08
    CYCLE_OUTDOOR = 0x09
    CYCLE = 0x0A
    AEROBIC_WORKOUT = 0x0B
    ELLIPTICAL = 0x0C
    SPORTS = 0x0D
    SWIM = 0x0E
    UNKNOWN = 0xFF


class PhysicalActivitySessionDescriptorData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Physical Activity Session Descriptor characteristic.

    Attributes:
        session_id: Session identifier.
        session_status: Status of the session.
        activity_type: Type of activity for this session (raw uint8).
        additional_data: Any additional descriptor bytes.

    """

    session_id: int
    session_status: PAMSessionStatus
    activity_type: ActivityType
    additional_data: bytes = b""


class PhysicalActivitySessionDescriptorCharacteristic(BaseCharacteristic[PhysicalActivitySessionDescriptorData]):
    """Physical Activity Session Descriptor characteristic (0x2B45).

    org.bluetooth.characteristic.physical_activity_session_descriptor

    Describes properties of an activity session.
    """

    min_length = 4  # session_id(2) + status(1) + activity_type(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PhysicalActivitySessionDescriptorData:
        """Parse Physical Activity Session Descriptor data.

        Format: SessionID (uint16 LE) + SessionStatus (uint8) + ActivityType (uint8)
                + AdditionalData (variable).
        """
        session_id = DataParser.parse_int16(data, 0, signed=False)
        session_status = PAMSessionStatus(DataParser.parse_int8(data, 2, signed=False))
        activity_type = ActivityType(DataParser.parse_int8(data, 3, signed=False))
        additional_data = bytes(data[4:])

        return PhysicalActivitySessionDescriptorData(
            session_id=session_id,
            session_status=session_status,
            activity_type=activity_type,
            additional_data=additional_data,
        )

    def _encode_value(self, data: PhysicalActivitySessionDescriptorData) -> bytearray:
        """Encode Physical Activity Session Descriptor data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.session_id, signed=False))
        result.extend(DataParser.encode_int8(int(data.session_status), signed=False))
        result.extend(DataParser.encode_int8(int(data.activity_type), signed=False))
        result.extend(data.additional_data)
        return result
