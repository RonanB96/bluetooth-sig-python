"""Object Type characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_UUID_16BIT_BYTES = 2
_UUID_128BIT_BYTES = 16
_UUID_16BIT_HEX_CHARS = 4
_UUID_128BIT_HEX_CHARS = 32


class ObjectTypeCharacteristic(BaseCharacteristic[str]):
    """Object Type characteristic (0x2ABF).

    org.bluetooth.characteristic.object_type

    A GATT UUID identifying the type of an object in the Object Transfer
    Service (OTS). May be a 16-bit (2 bytes) or 128-bit (16 bytes) UUID.
    """

    min_length: int = 2
    max_length: int = 16

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> str:
        """Parse object type UUID.

        Args:
            data: Raw bytes (2 or 16 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            UUID as uppercase hex string (e.g. "2AC3" or full 128-bit).

        """
        if len(data) == _UUID_16BIT_BYTES:
            raw = DataParser.parse_int16(data, 0, signed=False)
            return f"{raw:04X}"

        # 128-bit UUID: formatted as standard UUID string
        # Bytes are little-endian, standard UUID format is big-endian groups
        parts = [
            data[3::-1].hex(),  # time_low (4 bytes, reversed)
            data[5:3:-1].hex(),  # time_mid (2 bytes, reversed)
            data[7:5:-1].hex(),  # time_hi_and_version (2 bytes, reversed)
            data[8:10].hex(),  # clock_seq (2 bytes, big-endian)
            data[10:16].hex(),  # node (6 bytes, big-endian)
        ]
        return "-".join(parts).upper()

    def _encode_value(self, data: str) -> bytearray:
        """Encode object type UUID to bytes.

        Args:
            data: UUID as hex string (4 chars for 16-bit, or
                  standard UUID format for 128-bit).

        Returns:
            Encoded bytes (2 or 16 bytes).

        """
        clean = data.replace("-", "").replace(" ", "").upper()

        if len(clean) == _UUID_16BIT_HEX_CHARS:
            # 16-bit UUID
            value = int(clean, 16)
            return DataParser.encode_int16(value, signed=False)

        if len(clean) == _UUID_128BIT_HEX_CHARS:
            # 128-bit UUID: reverse byte order for BLE little-endian groups
            raw = bytes.fromhex(clean)
            result = bytearray()
            result.extend(raw[0:4][::-1])  # time_low reversed
            result.extend(raw[4:6][::-1])  # time_mid reversed
            result.extend(raw[6:8][::-1])  # time_hi_and_version reversed
            result.extend(raw[8:10])  # clock_seq big-endian
            result.extend(raw[10:16])  # node big-endian
            return result

        raise ValueError(f"UUID must be 4 hex chars (16-bit) or 32 hex chars (128-bit), got {len(clean)} chars")
