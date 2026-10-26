"""Registered User characteristic (0x2B37).

Segmented user registration data.

References:
    Bluetooth SIG User Data Service 1.0
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RegisteredUserData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Registered User.

    Attributes:
        segment_index: Segment index for multi-segment transfers.
        user_index: Index of the registered user.
        body: Variable-length user data body.

    """

    segment_index: int
    user_index: int
    body: bytes = b""


class RegisteredUserCharacteristic(BaseCharacteristic[RegisteredUserData]):
    """Registered User characteristic (0x2B37).

    org.bluetooth.characteristic.registered_user

    User registration data with segmentation support. Each notification
    carries a segment index, user index, and variable-length body.
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RegisteredUserData:
        """Parse Registered User data.

        Format: Segment Index (uint8) + User Index (uint8) + Body (variable).
        """
        segment_index = DataParser.parse_int8(data, 0, signed=False)
        user_index = DataParser.parse_int8(data, 1, signed=False)
        body = bytes(data[2:])

        return RegisteredUserData(
            segment_index=segment_index,
            user_index=user_index,
            body=body,
        )

    def _encode_value(self, data: RegisteredUserData) -> bytearray:
        """Encode Registered User data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.segment_index, signed=False))
        result.extend(DataParser.encode_int8(data.user_index, signed=False))
        result.extend(data.body)
        return result
