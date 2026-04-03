"""Types for the Binary Sensor Service (BSS).

References:
    Bluetooth SIG Binary Sensor Service 1.0, Sections 3.1.1.1 and 4.2.1
"""

from __future__ import annotations

from enum import IntEnum

import msgspec


class BSSMessageID(IntEnum):
    """BSS Message IDs as per BSS v1.0 Table 4.3."""

    GET_SENSOR_STATUS_COMMAND = 0x00
    GET_SENSOR_STATUS_RESPONSE = 0x01
    SETTING_SENSOR_COMMAND = 0x02
    SETTING_SENSOR_RESPONSE = 0x03
    SENSOR_STATUS_EVENT = 0x04


class SplitHeader(msgspec.Struct, frozen=True, kw_only=True):
    """BSS Split Header as per BSS v1.0 Table 3.3.

    Bit layout (uint8):
        Bit 0: Execute Flag (1 = final/non-split, 0 = split packet)
        Bits 1-5: Sequence Number (0-31)
        Bit 6: RFU
        Bit 7: Source Flag (0 = client→server, 1 = server→client)

    Attributes:
        execute_flag: True if this is the final (or only) packet.
        sequence_number: Sequence order of split packets (0-31).
        source_flag: True if direction is server→client.

    """

    execute_flag: bool
    sequence_number: int
    source_flag: bool

    _EXECUTE_FLAG_MASK = 0x01
    _SEQUENCE_NUMBER_MASK = 0x1F
    _SEQUENCE_NUMBER_SHIFT = 1
    _SOURCE_FLAG_MASK = 0x80
    _SOURCE_FLAG_SHIFT = 7

    @staticmethod
    def from_byte(value: int) -> SplitHeader:
        """Parse a Split Header from a raw uint8."""
        return SplitHeader(
            execute_flag=bool(value & SplitHeader._EXECUTE_FLAG_MASK),
            sequence_number=(value >> SplitHeader._SEQUENCE_NUMBER_SHIFT) & SplitHeader._SEQUENCE_NUMBER_MASK,
            source_flag=bool(value & SplitHeader._SOURCE_FLAG_MASK),
        )

    def to_byte(self) -> int:
        """Encode the Split Header to a raw uint8."""
        return (
            (int(self.execute_flag) & self._EXECUTE_FLAG_MASK)
            | ((self.sequence_number & self._SEQUENCE_NUMBER_MASK) << self._SEQUENCE_NUMBER_SHIFT)
            | ((int(self.source_flag) & self._EXECUTE_FLAG_MASK) << self._SOURCE_FLAG_SHIFT)
        )
