"""CardioRespiratory Activity Summary Data characteristic (0x2B3F)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CardioRespiratorySummaryFlags(IntFlag):
    """Flags for CardioRespiratory Activity Summary Data (Table 3.13)."""

    TIME_IN_HR_ZONE1_PRESENT = 0x00000001
    TIME_IN_HR_ZONE2_PRESENT = 0x00000002
    TIME_IN_HR_ZONE3_PRESENT = 0x00000004
    TIME_IN_HR_ZONE4_PRESENT = 0x00000008
    TIME_IN_HR_ZONE5_PRESENT = 0x00000010
    MIN_VO2_MAX_PRESENT = 0x00000020
    MAX_VO2_MAX_PRESENT = 0x00000040
    AVG_VO2_MAX_PRESENT = 0x00000080
    MIN_HEART_RATE_PRESENT = 0x00000100
    MAX_HEART_RATE_PRESENT = 0x00000200
    AVG_HEART_RATE_PRESENT = 0x00000400
    MIN_PULSE_IBI_PRESENT = 0x00000800
    MAX_PULSE_IBI_PRESENT = 0x00001000
    AVG_PULSE_IBI_PRESENT = 0x00002000
    MIN_RESTING_HR_PRESENT = 0x00004000
    MAX_RESTING_HR_PRESENT = 0x00008000
    AVG_RESTING_HR_PRESENT = 0x00010000
    MIN_HRV_PRESENT = 0x00020000
    MAX_HRV_PRESENT = 0x00040000
    AVG_HRV_PRESENT = 0x00080000
    MIN_RESPIRATION_RATE_PRESENT = 0x00100000
    MAX_RESPIRATION_RATE_PRESENT = 0x00200000
    AVG_RESPIRATION_RATE_PRESENT = 0x00400000
    MIN_RESTING_RESP_PRESENT = 0x00800000
    MAX_RESTING_RESP_PRESENT = 0x01000000
    AVG_RESTING_RESP_PRESENT = 0x02000000
    WORN_DURATION_PRESENT = 0x04000000


class CardioRespiratoryActivitySummaryData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from CardioRespiratory Activity Summary Data.

    Contains flags and any additional summary field data as raw bytes.
    The flags field indicates which optional fields are present.
    """

    flags: CardioRespiratorySummaryFlags
    additional_data: bytes = b""


_FLAGS_SIZE = 4  # flags field (uint32)


class CardioRespiratoryActivitySummaryDataCharacteristic(
    BaseCharacteristic[CardioRespiratoryActivitySummaryData],
):
    """CardioRespiratory Activity Summary Data characteristic (0x2B3F).

    org.bluetooth.characteristic.cardiorespiratory_activity_summary_data

    Summary cardiorespiratory activity data from the Physical
    Activity Monitor service. Flags indicate which optional summary
    fields are present.
    """

    _characteristic_name = "CardioRespiratory Activity Summary Data"
    min_length = 4  # flags (uint32)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CardioRespiratoryActivitySummaryData:
        """Parse CardioRespiratory Activity Summary Data.

        Format: flags (uint32) + variable optional fields.
        """
        flags = CardioRespiratorySummaryFlags(DataParser.parse_int32(data, 0, signed=False))
        additional_data = bytes(data[_FLAGS_SIZE:]) if len(data) > _FLAGS_SIZE else b""

        return CardioRespiratoryActivitySummaryData(
            flags=flags,
            additional_data=additional_data,
        )

    def _encode_value(self, data: CardioRespiratoryActivitySummaryData) -> bytearray:
        """Encode CardioRespiratory Activity Summary Data to bytes."""
        result = bytearray()
        result += DataParser.encode_int32(int(data.flags), signed=False)
        result += bytearray(data.additional_data)
        return result
