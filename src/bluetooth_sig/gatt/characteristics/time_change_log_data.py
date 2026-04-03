"""Time Change Log Data characteristic (0x2B92).

Variable-length time change records.

References:
    Bluetooth SIG Device Time Service specification
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class TimeChangeLogDataCharacteristic(BaseCharacteristic[bytes]):
    """Time Change Log Data characteristic (0x2B92).

    org.bluetooth.characteristic.time_change_log_data

    Variable-length records documenting time changes on the device.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
