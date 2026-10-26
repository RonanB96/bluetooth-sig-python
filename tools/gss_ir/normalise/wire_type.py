"""Fixed-width wire types accepted by schema version 1."""

from __future__ import annotations

from tools.gss_ir.v1 import BITS_PER_OCTET, WIRE_SIZE_BYTES, WireType

from .result import Unsupported
from .subbyte import subbyte_domain

_RULE = "wire_type"
# GSS writes ``boolean[N]`` and ``int16``. The IR stores the wire type name.
_WIRE_ALIASES: dict[str, WireType] = {
    "boolean[8]": WireType.BOOLEAN8,
    "boolean[16]": WireType.BOOLEAN16,
    "boolean[24]": WireType.BOOLEAN24,
    "boolean[32]": WireType.BOOLEAN32,
    "int16": WireType.SINT16,
}
_REAL_WIRE = frozenset({WireType.MEDFLOAT16, WireType.MEDFLOAT32, WireType.FLOAT32})
_BOOLEAN_WIRE = frozenset({WireType.BOOLEAN8, WireType.BOOLEAN16, WireType.BOOLEAN24, WireType.BOOLEAN32})
_UNSIGNED_WIRE = frozenset(
    {
        WireType.UINT8,
        WireType.UINT16,
        WireType.UINT24,
        WireType.UINT32,
        WireType.UINT48,
        WireType.UINT64,
    }
)
_SIGNED_WIRE = frozenset({WireType.SINT8, WireType.SINT16, WireType.SINT24, WireType.SINT32})
_SUBBYTE_WIRE = frozenset({WireType.UINT1, WireType.UINT2})
OUTSIDE_WIRE_PREFIX = "endpoints do not fit "


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


def integer_domain(wire: WireType) -> tuple[int, int] | None:
    """Return the inclusive raw domain of an integer wire.

    Args:
        wire: Wire type already accepted for a field.

    Returns:
        Inclusive minimum and maximum, or ``None`` for UTF-8, boolean, and real wires.
    """
    if wire in _SUBBYTE_WIRE:
        return subbyte_domain(wire)
    if wire not in _UNSIGNED_WIRE and wire not in _SIGNED_WIRE:
        return None
    bits = WIRE_SIZE_BYTES[wire] * BITS_PER_OCTET
    if wire in _SIGNED_WIRE:
        return (-(1 << (bits - 1)), (1 << (bits - 1)) - 1)
    return (0, (1 << bits) - 1)


def outside_wire_detail(wire: WireType) -> str:
    """Describe an integer range that does not fit ``wire``.

    Args:
        wire: Integer wire whose domain rejects the stored endpoints.

    Returns:
        The stable detail stored on the unsupported result.
    """
    return f"{OUTSIDE_WIRE_PREFIX}{wire.value}"


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
    bits = WIRE_SIZE_BYTES[wire] * BITS_PER_OCTET
    return (0, (1 << bits) - 1)
