"""Call Control Point Optional Opcodes characteristic (0x2BBF)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class CallControlPointOptionalOpcodes(IntFlag):
    """Optional opcodes supported by the Call Control Point."""

    LOCAL_HOLD_AND_LOCAL_RETRIEVE = 0x0001
    JOIN = 0x0002


class CallControlPointOptionalOpcodesCharacteristic(
    BaseCharacteristic[CallControlPointOptionalOpcodes],
):
    """Call Control Point Optional Opcodes characteristic (0x2BBF).

    org.bluetooth.characteristic.call_control_point_optional_opcodes

    Bitmask of optional opcodes supported by the Call Control Point.
    """

    expected_length: int = 2
    _template = FlagTemplate.uint16(CallControlPointOptionalOpcodes)
