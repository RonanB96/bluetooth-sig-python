"""BR-EDR Handover Data characteristic (0x2B38).

Variable-length raw bytes for BR/EDR handover information.

References:
    Bluetooth SIG Handover Profile specification
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class BREDRHandoverDataCharacteristic(BaseCharacteristic[bytes]):
    """BR-EDR Handover Data characteristic (0x2B38).

    org.bluetooth.characteristic.br_edr_handover_data

    Variable-length opaque data used during BR/EDR handover procedures.
    """

    _characteristic_name = "BR-EDR Handover Data"
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
