"""Physical Activity Current Session characteristic (0x2B44).

Contains current session data including activity type and session start indicator.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class PAMSessionFlags(IntFlag):
    """Physical Activity Current Session flags."""

    SESSION_ACTIVE = 0x01
    ACTIVITY_TYPE_PRESENT = 0x02


class PAMActivityType(IntEnum):
    """Physical Activity Monitor activity types."""

    NO_ACTIVITY = 0x00
    WALKING = 0x01
    RUNNING = 0x02
    CYCLING = 0x03
    SWIMMING = 0x04
    GENERIC = 0xFF


_ACTIVITY_TYPE_MINIMUM_LENGTH = 4


class PhysicalActivityCurrentSessionData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Physical Activity Current Session characteristic.

    Attributes:
        flags: Session presence flags.
        session_id: Session identifier.
        activity_type: Type of physical activity. None if not present.

    """

    flags: PAMSessionFlags
    session_id: int
    activity_type: PAMActivityType | None = None


class PhysicalActivityCurrentSessionCharacteristic(BaseCharacteristic[PhysicalActivityCurrentSessionData]):
    """Physical Activity Current Session characteristic (0x2B44).

    org.bluetooth.characteristic.physical_activity_current_session

    Reports the current session information for the Physical Activity Monitor.
    """

    min_length = 3  # flags(1) + session_id(2)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PhysicalActivityCurrentSessionData:
        """Parse Physical Activity Current Session data.

        Format: Flags (uint8) + SessionID (uint16 LE) + [ActivityType (uint8)].
        """
        flags = PAMSessionFlags(DataParser.parse_int8(data, 0, signed=False))
        session_id = DataParser.parse_int16(data, 1, signed=False)

        activity_type: PAMActivityType | None = None
        if flags & PAMSessionFlags.ACTIVITY_TYPE_PRESENT and len(data) >= _ACTIVITY_TYPE_MINIMUM_LENGTH:
            activity_type = PAMActivityType(DataParser.parse_int8(data, 3, signed=False))

        return PhysicalActivityCurrentSessionData(
            flags=flags,
            session_id=session_id,
            activity_type=activity_type,
        )

    def _encode_value(self, data: PhysicalActivityCurrentSessionData) -> bytearray:
        """Encode Physical Activity Current Session data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(DataParser.encode_int16(data.session_id, signed=False))
        if data.activity_type is not None:
            result.extend(DataParser.encode_int8(int(data.activity_type), signed=False))
        return result
