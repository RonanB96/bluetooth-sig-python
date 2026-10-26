"""ESL Response Key Material characteristic (0x2BF8).

Contains the 128-bit key material used by an ESL to encrypt and
authenticate response data sent back to the ESL Access Point.

References:
    Bluetooth SIG Electronic Shelf Label Profile, §3.7.2
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ESLResponseKeyMaterialCharacteristic(BaseCharacteristic[bytes]):
    """ESL Response Key Material characteristic (0x2BF8).

    org.bluetooth.characteristic.esl_response_key_material

    128-bit (16 byte) key material for ESL response encryption.
    Written by the ESL Access Point during the configuration procedure.
    """

    _characteristic_name = "ESL Response Key Material"
    _manual_role = CharacteristicRole.INFO
    expected_length: int = 16  # 128-bit key
    min_length: int = 16

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> bytes:
        """Parse ESL response key material (16 bytes).

        Args:
            data: Raw bytes (16 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate (default True).

        Returns:
            Raw 128-bit key material as bytes.

        """
        return bytes(data[:16])

    def _encode_value(self, data: bytes) -> bytearray:
        """Encode ESL response key material to bytes.

        Args:
            data: 16-byte key material.

        Returns:
            Encoded bytes (16 bytes).

        """
        return bytearray(data)
