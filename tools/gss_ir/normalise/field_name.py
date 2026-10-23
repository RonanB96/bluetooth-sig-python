"""Field names in snake_case."""

from __future__ import annotations

import re

from .result import Unsupported

_RULE = "field_name"
_PARENTHETICAL = re.compile(r"\([^)]*\)")
_SEPARATORS = re.compile(r"[\s\-]+")
_NON_WORD = re.compile(r"[^\w]")
_REPEATED_UNDERSCORE = re.compile(r"_+")
_SNAKE = re.compile(r"[a-z][a-z0-9_]*\Z")


def parse_field_name(label: str) -> str | Unsupported:
    """Convert a SIG field label to ``snake_case``.

    Args:
        label: Raw ``field`` string from a characteristic structure.

    Returns:
        The snake_case name, or an unsupported result when the label has no name.
    """
    name = label.lower()
    name = _PARENTHETICAL.sub("", name)
    name = _SEPARATORS.sub("_", name)
    name = _NON_WORD.sub("", name)
    name = _REPEATED_UNDERSCORE.sub("_", name).strip("_")
    if _SNAKE.fullmatch(name) is None:
        return Unsupported(rule=_RULE, detail=f"field name {label!r} is not snake_case")
    return name
