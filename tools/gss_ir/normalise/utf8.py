"""UTF-8 wire types ``utf8s`` and ``utf8s{N}``."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .result import Unsupported

_RULE = "utf8"
# GSS escapes the braces: ``utf8s\{16\}``. ``N`` is one parameter, not a type per width.
_UTF8 = re.compile(r"utf8s(?:\\\{(?P<octets>[1-9]\d*)\\\})?\Z")


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


def parse_utf8_size(size: str, capacity: int | None) -> int | Unsupported | None:
    """Accept the size text that matches this UTF-8 type.

    Variable ``utf8s`` repeats as size ``variable``. ``utf8s{N}`` repeats as
    the decimal size ``N``.

    Args:
        size: Raw ``size`` string.
        capacity: ``N`` from the type, or ``None`` for variable ``utf8s``.

    Returns:
        ``None`` for a variable string, ``N`` when the size agrees with the
        type parameter, or an unsupported result.
    """
    if capacity is None:
        if size == "variable":
            return None
        return Unsupported(rule=_RULE, detail=f"size {size!r} is not variable")
    if size != str(capacity):
        return Unsupported(rule=_RULE, detail=f"size {size!r} disagrees with utf8 capacity {capacity}")
    return capacity
