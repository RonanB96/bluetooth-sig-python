"""Fixed-width wire types accepted by schema version 1."""

from __future__ import annotations

from tools.gss_ir.v1 import WIRE_SIZE_BYTES, WireType

from .result import Unsupported

_RULE = "wire_type"
# GSS writes ``boolean[N]`` and ``int16``. The IR stores a C++ enumerator name.
_WIRE_ALIASES: dict[str, WireType] = {
    "boolean[8]": WireType.BOOLEAN8,
    "boolean[16]": WireType.BOOLEAN16,
    "boolean[24]": WireType.BOOLEAN24,
    "boolean[32]": WireType.BOOLEAN32,
    "int16": WireType.SINT16,
}
_REAL_WIRE = frozenset({WireType.MEDFLOAT16, WireType.MEDFLOAT32, WireType.FLOAT32})
_BOOLEAN_WIRE = frozenset({WireType.BOOLEAN8, WireType.BOOLEAN16, WireType.BOOLEAN24, WireType.BOOLEAN32})


def parse_wire_type(type_text: str) -> WireType | Unsupported:
    """Accept a fixed-width ADR-0003 wire type.

    Args:
        type_text: Raw ``type`` string from a characteristic structure.

    Returns:
        The wire type, or an unsupported result for any other type string.
        ``boolean[N]`` and ``int16`` are stored under their IR names.
    """
    text = type_text.strip()
    alias = _WIRE_ALIASES.get(text)
    if alias is not None:
        return alias
    try:
        return WireType(text)
    except ValueError:
        return Unsupported(rule=_RULE, detail=f"unsupported wire type {type_text!r}")


def implicit_raw_domain(wire: WireType) -> tuple[int, int] | None:
    """Return the full raw domain when a description has no numeric range.

    Boolean fields and IEEE floats in the GSS corpus state bits or special
    values instead of an allowed range. The domain is every bit pattern of
    the wire width. Other wire types stay unsupported until a range is parsed.

    Args:
        wire: Wire type already accepted for this field.

    Returns:
        Inclusive raw minimum and maximum, or ``None`` when a range sentence
        is required.
    """
    if wire not in _BOOLEAN_WIRE and wire not in _REAL_WIRE:
        return None
    bits = WIRE_SIZE_BYTES[wire] * 8
    return (0, (1 << bits) - 1)
