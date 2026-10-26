"""UTF-8 wire types ``utf8s`` and ``utf8s{N}``."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .result import Unsupported

_RULE = "utf8"
# Bluetooth Core Specification v5.4, Vol 3, Part F, 3.2.9.
ATT_MAX_VALUE_OCTETS = 512
# GSS escapes the braces: ``utf8s\{16\}``. ``N`` is one parameter, not a type per width.
_UTF8 = re.compile(r"utf8s(?:\\\{(?P<octets>[1-9]\d*)\\\})?\Z")
# GSS writes the range with an en dash. Hyphen and em dash are the same range.
_RANGE = re.compile(r"0\s*[\u2013\u2014-]\s*(?P<octets>[1-9]\d*)\Z")
_VARIABLE_AND_RANGE_LINES = 2


@dataclass(frozen=True, kw_only=True)
class Utf8Type:
    """A UTF-8 field.

    ``capacity`` is ``None`` for ``utf8s`` and ``N`` for ``utf8s{N}``.
    """

    capacity: int | None


def parse_utf8_type(type_text: str) -> Utf8Type | None:
    """Accept ``utf8s`` or ``utf8s{N}``.

    Args:
        type_text: Raw ``type`` string.

    Returns:
        The UTF-8 type, or ``None`` when the text is a different wire type.
    """
    match = _UTF8.fullmatch(type_text.strip())
    if match is None:
        return None
    octets = match.group("octets")
    if octets is None:
        return Utf8Type(capacity=None)
    return Utf8Type(capacity=int(octets))


def _range_maximum(text: str) -> int | Unsupported | None:
    match = _RANGE.fullmatch(text.strip())
    if match is None:
        return None
    octets = int(match.group("octets"))
    if octets > ATT_MAX_VALUE_OCTETS:
        return Unsupported(
            rule=_RULE,
            detail=f"utf8 maximum {octets} exceeds {ATT_MAX_VALUE_OCTETS} octets",
        )
    return octets


def parse_utf8_size(size: str, capacity: int | None) -> int | Unsupported | None:
    """Accept the size text that matches this UTF-8 type.

    ``utf8s{N}`` repeats as the decimal size ``N`` and means at most ``N`` octets.
    Variable ``utf8s`` repeats as size ``variable``, or as a range from 0 to N
    when the characteristic states a maximum. A size of ``variable`` followed by
    that range on the next line is the same maximum.

    Args:
        size: Raw ``size`` string.
        capacity: ``N`` from the type, or ``None`` for variable ``utf8s``.

    Returns:
        ``None`` when the characteristic states no maximum, the octet maximum
        otherwise, or an unsupported result.
    """
    text = size.strip()
    if capacity is None:
        if text == "variable":
            return None
        ranged = _range_maximum(text)
        if isinstance(ranged, Unsupported):
            return ranged
        if ranged is not None:
            return ranged
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) == _VARIABLE_AND_RANGE_LINES and lines[0] == "variable":
            ranged = _range_maximum(lines[1])
            if isinstance(ranged, Unsupported):
                return ranged
            if ranged is not None:
                return ranged
        return Unsupported(rule=_RULE, detail=f"size {size!r} is not variable")
    if text != str(capacity):
        return Unsupported(rule=_RULE, detail=f"size {size!r} disagrees with utf8 capacity {capacity}")
    return capacity
