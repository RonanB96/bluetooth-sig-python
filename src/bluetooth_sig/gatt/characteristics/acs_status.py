"""ACS Status characteristic (0x2B2F).

Reports the presence status of hearing aids.

References:
    Bluetooth SIG Audio Control Service
"""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class ACSHearingAidPresence(IntEnum):
    """ACS hearing aid presence status values."""

    NO_HEARING_AID_PRESENT = 0x00
    LEFT_PRESENT = 0x01
    RIGHT_PRESENT = 0x02
    BOTH_PRESENT = 0x03


class ACSStatusCharacteristic(BaseCharacteristic[ACSHearingAidPresence]):
    """ACS Status characteristic (0x2B2F).

    org.bluetooth.characteristic.acs_status

    Reports the presence status of hearing aids.
    """

    _template = EnumTemplate.uint8(ACSHearingAidPresence)

    min_value: int = ACSHearingAidPresence.NO_HEARING_AID_PRESENT  # 0
    max_value: int = ACSHearingAidPresence.BOTH_PRESENT  # 3
