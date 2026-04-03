"""Database Hash characteristic (0x2B2A)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class DatabaseHashCharacteristic(BaseCharacteristic[bytes]):
    """Database Hash characteristic (0x2B2A).

    org.bluetooth.characteristic.database_hash

    128-bit (16-byte) hash of the GATT database.
    """

    expected_length: int = 16

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data[:16])

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data[:16].ljust(16, b"\x00"))
