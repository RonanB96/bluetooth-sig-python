"""Set Identity Resolving Key characteristic (0x2B84).

16-byte Set Identity Resolving Key (SIRK) for CSIP.

References:
    Bluetooth SIG Coordinated Set Identification Service 1.0
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class SetIdentityResolvingKeyCharacteristic(BaseCharacteristic[bytes]):
    """Set Identity Resolving Key characteristic (0x2B84).

    org.bluetooth.characteristic.set_identity_resolving_key

    16-byte Set Identity Resolving Key used by the Coordinated Set
    Identification Service for set member resolution.
    """

    expected_length = 16

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data[:16])

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data[:16].ljust(16, b"\x00"))
