"""Emergency ID characteristic (0x2B2D)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic

_EMERGENCY_ID_LENGTH = 6


class EmergencyIdCharacteristic(BaseCharacteristic[bytes]):
    """Emergency ID characteristic (0x2B2D).

    org.bluetooth.characteristic.emergency_id

    6-octet identifier: the first 48 bits of a randomly generated 128-bit
    number. Assigned at manufacture or provisioning; static for the lifetime
    of the device. Read-only, encryption required.
    """

    expected_length: int = _EMERGENCY_ID_LENGTH
    min_length: int = _EMERGENCY_ID_LENGTH

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data[:_EMERGENCY_ID_LENGTH])

    def _encode_value(self, data: bytes) -> bytearray:
        if len(data) != _EMERGENCY_ID_LENGTH:
            msg = f"Emergency ID must be exactly {_EMERGENCY_ID_LENGTH} bytes, got {len(data)}"
            raise ValueError(msg)
        return bytearray(data)
