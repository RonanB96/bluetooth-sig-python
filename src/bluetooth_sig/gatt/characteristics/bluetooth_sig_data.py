"""Bluetooth SIG Data characteristic (0x2B39).

Variable-length opaque data defined by Bluetooth SIG.

References:
    Bluetooth SIG Handover Profile specification
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class BluetoothSIGDataCharacteristic(BaseCharacteristic[bytes]):
    """Bluetooth SIG Data characteristic (0x2B39).

    org.bluetooth.characteristic.bluetooth_sig_data

    Variable-length opaque data block defined by Bluetooth SIG.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
