"""AP Sync Key Material characteristic (0x2BF7).

16-byte key material for AP synchronisation.

References:
    Bluetooth SIG Common Audio Profile specification
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class APSyncKeyMaterialCharacteristic(BaseCharacteristic[bytes]):
    """AP Sync Key Material characteristic (0x2BF7).

    org.bluetooth.characteristic.ap_sync_key_material

    16-byte key material used for audio profile synchronisation.
    """

    expected_length = 16

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data[:16])

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data[:16].ljust(16, b"\x00"))
