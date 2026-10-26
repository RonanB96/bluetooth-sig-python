"""CardioRespiratory Activity Instantaneous Data characteristic (0x2B3E)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CardioRespiratoryInstantaneousFlags(IntFlag):
    """Flags for CardioRespiratory Activity Instantaneous Data (Table 3.11)."""

    VO2_MAX_PRESENT = 0x0001
    HEART_RATE_PRESENT = 0x0002
    PULSE_INTER_BEAT_INTERVAL_PRESENT = 0x0004
    RESTING_HEART_RATE_PRESENT = 0x0008
    HEART_RATE_VARIABILITY_PRESENT = 0x0010
    RESPIRATION_RATE_PRESENT = 0x0020
    RESTING_RESPIRATION_RATE_PRESENT = 0x0040
    DEVICE_WORN = 0x8000


class CardioRespiratoryActivityInstantaneousData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from CardioRespiratory Activity Instantaneous Data.

    Contains flags and any additional field data as raw bytes.
    The flags field indicates which optional fields are present.
    """

    flags: CardioRespiratoryInstantaneousFlags
    additional_data: bytes = b""


_FLAGS_SIZE = 2  # flags field (uint16)


class CardioRespiratoryActivityInstantaneousDataCharacteristic(
    BaseCharacteristic[CardioRespiratoryActivityInstantaneousData],
):
    """CardioRespiratory Activity Instantaneous Data characteristic (0x2B3E).

    org.bluetooth.characteristic.cardiorespiratory_activity_instantaneous_data

    Instantaneous cardiorespiratory activity data from the Physical
    Activity Monitor service. Flags indicate which optional fields
    (heart rate, resting heart rate, cadence, distance, etc.) are present.
    """

    _characteristic_name = "CardioRespiratory Activity Instantaneous Data"
    min_length = 2  # flags (uint16)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CardioRespiratoryActivityInstantaneousData:
        """Parse CardioRespiratory Activity Instantaneous Data.

        Format: flags (uint16) + variable optional fields.
        """
        flags = CardioRespiratoryInstantaneousFlags(DataParser.parse_int16(data, 0, signed=False))
        additional_data = bytes(data[_FLAGS_SIZE:]) if len(data) > _FLAGS_SIZE else b""

        return CardioRespiratoryActivityInstantaneousData(
            flags=flags,
            additional_data=additional_data,
        )

    def _encode_value(self, data: CardioRespiratoryActivityInstantaneousData) -> bytearray:
        """Encode CardioRespiratory Activity Instantaneous Data to bytes."""
        result = bytearray()
        result += DataParser.encode_int16(int(data.flags), signed=False)
        result += bytearray(data.additional_data)
        return result
