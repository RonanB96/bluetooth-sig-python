"""Authorization Control Service shared data types."""

from __future__ import annotations

import msgspec

MAX_ROLLING_SEGMENT_COUNTER = 0x3F


class ACSSegmentationHeader(msgspec.Struct, frozen=True, kw_only=True):
    """Segmentation header for ACS segmented values."""

    first_segment: bool
    last_segment: bool
    rolling_segment_counter: int


class ACSDataPacket(msgspec.Struct, frozen=True, kw_only=True):
    """Segmented ACS payload container."""

    header: ACSSegmentationHeader
    payload: bytes


class ACSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ACS Control Point characteristic."""

    header: ACSSegmentationHeader
    opcode: int
    operand: bytes = b""
