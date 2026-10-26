"""Pushbutton Status 8 characteristic (0x2C21).

Represents the status of up to 4 pushbuttons packed into a single byte.
Each button occupies 2 bits, yielding four independent status values.
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser

_BUTTON_MASK = 0x03


class ButtonStatus(IntEnum):
    """Status of an individual pushbutton.

    Values:
        NOT_ACTUATED: Button not actuated or not in use (0)
        PRESSED: Button pressed (1)
        RELEASED: Button released (2)
        RESERVED: Reserved for future use (3)
    """

    NOT_ACTUATED = 0
    PRESSED = 1
    RELEASED = 2
    RESERVED = 3


class PushbuttonStatus8Data(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded pushbutton status for four buttons."""

    button_0: ButtonStatus
    button_1: ButtonStatus
    button_2: ButtonStatus
    button_3: ButtonStatus


class PushbuttonStatus8Characteristic(BaseCharacteristic[PushbuttonStatus8Data]):
    """Pushbutton Status 8 characteristic (0x2C21).

    org.bluetooth.characteristic.pushbutton_status_8

    Four independent 2-bit button status fields packed into a single byte.
    Bits [1:0] → Button 0, [3:2] → Button 1, [5:4] → Button 2, [7:6] → Button 3.
    """

    expected_length = 1

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> PushbuttonStatus8Data:
        """Decode four 2-bit button status fields from a single byte."""
        raw = DataParser.parse_int8(data, 0, signed=False)

        return PushbuttonStatus8Data(
            button_0=ButtonStatus((raw >> 0) & _BUTTON_MASK),
            button_1=ButtonStatus((raw >> 2) & _BUTTON_MASK),
            button_2=ButtonStatus((raw >> 4) & _BUTTON_MASK),
            button_3=ButtonStatus((raw >> 6) & _BUTTON_MASK),
        )

    def _encode_value(self, data: PushbuttonStatus8Data) -> bytearray:
        """Encode four button statuses into a single byte."""
        encoded = (
            (data.button_0 & _BUTTON_MASK)
            | ((data.button_1 & _BUTTON_MASK) << 2)
            | ((data.button_2 & _BUTTON_MASK) << 4)
            | ((data.button_3 & _BUTTON_MASK) << 6)
        )
        return DataParser.encode_int8(encoded, signed=False)
