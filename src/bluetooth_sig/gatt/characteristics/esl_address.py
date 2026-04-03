"""ESL Address characteristic implementation.

Per ESL Service v1.0 §3.1.1, the ESL Address is a 16-bit value:
  - Bits 0-7: ESL_ID (8-bit, range 0x00-0xFE; 0xFF = Broadcast Address)
  - Bits 8-14: Group_ID (7-bit, range 0-127)
  - Bit 15: RFU (Reserved for Future Use)
"""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

ESL_ID_MASK = 0x00FF
GROUP_ID_MASK = 0x7F00
GROUP_ID_SHIFT = 8


class ESLAddressData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed ESL Address fields.

    Attributes:
        esl_id: ESL identifier (bits 0-7, range 0x00-0xFF).
        group_id: Group identifier (bits 8-14, range 0-127).
    """

    esl_id: int
    group_id: int


class ESLAddressCharacteristic(BaseCharacteristic[ESLAddressData]):
    """ESL Address characteristic (0x2BF6).

    org.bluetooth.characteristic.esl_address

    A 16-bit ESL address where bits 0-7 are the ESL ID, bits 8-14 are
    the Group ID, and bit 15 is reserved for future use (RFU).
    """

    _manual_role = CharacteristicRole.INFO
    expected_length: int = 2
    min_length: int = 2

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ESLAddressData:
        """Parse ESL address into ESL_ID and Group_ID fields.

        Args:
            data: Raw bytes (2 bytes, little-endian uint16).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLAddressData with esl_id and group_id.

        """
        raw = DataParser.parse_int16(data, 0, signed=False)
        return ESLAddressData(
            esl_id=raw & ESL_ID_MASK,
            group_id=(raw & GROUP_ID_MASK) >> GROUP_ID_SHIFT,
        )

    def _encode_value(self, data: ESLAddressData) -> bytearray:
        """Encode ESL address fields to bytes.

        Args:
            data: ESLAddressData with esl_id and group_id.

        Returns:
            Encoded bytes (2 bytes, little-endian uint16).

        """
        raw = (data.esl_id & ESL_ID_MASK) | ((data.group_id << GROUP_ID_SHIFT) & GROUP_ID_MASK)
        return DataParser.encode_int16(raw, signed=False)
