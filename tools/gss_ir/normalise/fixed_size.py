"""Fixed field sizes that agree with the wire width."""

from __future__ import annotations

import re

from tools.gss_ir.v1 import WIRE_SIZE_BYTES, WireType

from .result import Unsupported

_RULE = "fixed_size"
_INTEGER = re.compile(r"\d+\Z")


def parse_fixed_size(size: str, wire: WireType) -> int | Unsupported:
    """Accept a single integer size that matches the wire width.

    Args:
        size: Raw ``size`` string.
        wire: Wire type already accepted for this field.

    Returns:
        The size in bytes, or an unsupported result.
    """
    if _INTEGER.fullmatch(size) is None:
        return Unsupported(rule=_RULE, detail=f"size {size!r} is not a single integer")
    width = int(size)
    expected = WIRE_SIZE_BYTES[wire]
    # System ID records the EUI-64 width as 64 bits (system_id.yaml, size "64").
    if wire is WireType.UINT64 and width == expected * 8:
        return expected
    if width != expected:
        return Unsupported(
            rule=_RULE,
            detail=f"size {width} disagrees with {wire.value} width {expected}",
        )
    return width
