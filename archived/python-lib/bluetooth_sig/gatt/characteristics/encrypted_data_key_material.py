"""Encrypted Data Key Material characteristic (0x2B88).

Session key (16 bytes) + initialisation vector (8 bytes) for encrypted data.

References:
    Bluetooth SIG Encrypted Advertising Data specification
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class EncryptedDataKeyMaterialData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Encrypted Data Key Material.

    Attributes:
        session_key: 16-byte session key.
        iv: 8-byte initialisation vector.

    """

    session_key: bytes
    iv: bytes


class EncryptedDataKeyMaterialCharacteristic(BaseCharacteristic[EncryptedDataKeyMaterialData]):
    """Encrypted Data Key Material characteristic (0x2B88).

    org.bluetooth.characteristic.encrypted_data_key_material

    Contains the session key and initialisation vector for encrypted
    advertising data.
    """

    expected_length = 24

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> EncryptedDataKeyMaterialData:
        """Parse Encrypted Data Key Material.

        Format: Session Key (16 bytes) + IV (8 bytes).
        """
        session_key = bytes(data[:16])
        iv = bytes(data[16:24])

        return EncryptedDataKeyMaterialData(
            session_key=session_key,
            iv=iv,
        )

    def _encode_value(self, data: EncryptedDataKeyMaterialData) -> bytearray:
        """Encode Encrypted Data Key Material."""
        result = bytearray()
        result.extend(data.session_key[:16].ljust(16, b"\x00"))
        result.extend(data.iv[:8].ljust(8, b"\x00"))
        return result
