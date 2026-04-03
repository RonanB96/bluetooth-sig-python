"""Set Identity Resolving Key characteristic (0x2B84).

Type (1 byte) + 16-byte Set Identity Resolving Key (SIRK) for CSIP.

References:
    Bluetooth SIG Coordinated Set Identification Service 1.0, Section 3.1
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SIRKType(IntEnum):
    """SIRK type as per CSIS 1.0, Section 3.1."""

    ENCRYPTED = 0x00
    PLAIN_TEXT = 0x01


class SetIdentityResolvingKeyData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Set Identity Resolving Key characteristic."""

    sirk_type: SIRKType
    value: bytes


class SetIdentityResolvingKeyCharacteristic(BaseCharacteristic[SetIdentityResolvingKeyData]):
    """Set Identity Resolving Key characteristic (0x2B84).

    org.bluetooth.characteristic.set_identity_resolving_key

    Type (uint8: 0x00=Encrypted, 0x01=Plain text) followed by
    16-byte Set Identity Resolving Key used by the Coordinated Set
    Identification Service for set member resolution.
    """

    expected_length = 17

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SetIdentityResolvingKeyData:
        sirk_type = SIRKType(DataParser.parse_int8(data, 0, signed=False))
        value = bytes(data[1:17])

        return SetIdentityResolvingKeyData(sirk_type=sirk_type, value=value)

    def _encode_value(self, data: SetIdentityResolvingKeyData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.sirk_type), signed=False))
        result.extend(data.value[:16].ljust(16, b"\x00"))
        return result
