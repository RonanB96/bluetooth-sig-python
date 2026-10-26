"""Sub-byte unsigned wire types ``uintN`` for ``N`` below 8."""

from __future__ import annotations

import re

from tools.gss_ir.v1 import BITS_PER_OCTET, WireType

from .result import Unsupported

_RULE = "subbyte"
# Widths the corpus uses more than once. A ``uintN`` below one octet that is
# absent here stays unsupported.
_SUBBYTE_BITS: dict[WireType, int] = {
    WireType.UINT1: 1,
    WireType.UINT2: 2,
}
_WIRES = {bits: wire for wire, bits in _SUBBYTE_BITS.items()}
_UINT_N = re.compile(r"uint(?P<bits>[1-9]\d*)\Z")


def parse_subbyte_type(type_text: str) -> WireType | None:
    """Accept ``uintN`` when ``N`` is a sub-byte width used more than once.

    Args:
        type_text: Raw ``type`` string.

    Returns:
        The wire type, or ``None`` when the text is not a repeated sub-byte width.
    """
    match = _UINT_N.fullmatch(type_text.strip())
    if match is None:
        return None
    bits = int(match.group("bits"))
    if bits >= BITS_PER_OCTET:
        return None
    return _WIRES.get(bits)


def parse_subbyte_size(size: str, wire: WireType) -> int | Unsupported:
    """Accept a size equal to the bit width.

    Args:
        size: Raw ``size`` string.
        wire: Sub-byte wire type already accepted for this field.

    Returns:
        The width in bits, or an unsupported result.
    """
    bits = _SUBBYTE_BITS[wire]
    if size != str(bits):
        return Unsupported(rule=_RULE, detail=f"size {size!r} disagrees with {wire.value}")
    return bits


def subbyte_domain(wire: WireType) -> tuple[int, int]:
    """Return every value of a sub-byte unsigned field.

    Args:
        wire: Sub-byte wire type.

    Returns:
        Inclusive raw minimum and maximum.
    """
    bits = _SUBBYTE_BITS[wire]
    return (0, (1 << bits) - 1)
