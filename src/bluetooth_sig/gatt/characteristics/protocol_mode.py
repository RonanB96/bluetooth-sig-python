"""Protocol Mode characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class ProtocolMode(IntEnum):
    """Protocol Mode values."""

    BOOT_PROTOCOL = 0
    REPORT_PROTOCOL = 1


class ProtocolModeCharacteristic(BaseCharacteristic[int]):
    """Protocol Mode characteristic (0x2A4E).

    org.bluetooth.characteristic.protocol_mode

    Protocol Mode characteristic.
    """

    _python_type: type | str | None = int

    _template = EnumTemplate.uint8(ProtocolMode)

    # SIG spec: uint8 enumerated mode value → fixed 1-byte payload; no GSS YAML
    expected_length = 1
    min_length = 1
    max_length = 1
