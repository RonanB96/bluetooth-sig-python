"""Integer wire types accepted by schema version 1."""

from __future__ import annotations

from tools.gss_ir.v1 import WireType

from .result import Unsupported

_RULE = "wire_type"


def parse_wire_type(type_text: str) -> WireType | Unsupported:
    """Accept an ADR-0003 integer wire type.

    Args:
        type_text: Raw ``type`` string from a characteristic structure.

    Returns:
        The wire type, or an unsupported result for any other type string.
    """
    try:
        return WireType(type_text.strip())
    except ValueError:
        return Unsupported(rule=_RULE, detail=f"unsupported wire type {type_text!r}")
