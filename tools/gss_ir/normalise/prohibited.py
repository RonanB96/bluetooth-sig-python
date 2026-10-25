"""Prohibited and reserved text outside the declared range.

Those sentences are ``BTSIG_OUT_OF_RANGE`` at decode. They are not sentinels
and they are not IR fields.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .result import Unsupported

_RULE = "prohibited"
_KNOWN = (
    re.compile(r"All other values are prohibited\.?", re.IGNORECASE),
    re.compile(r"All other values are reserved for future use\.?", re.IGNORECASE),
)
_MENTION = re.compile(r"\b(?:prohibited|reserved)\b", re.IGNORECASE)


@dataclass(frozen=True, kw_only=True)
class OutsideRange:
    """A recognised prohibition that adds no IR member."""

    detail: str


def parse_prohibited(description: str) -> OutsideRange | Unsupported | None:
    """Recognise prohibited and reserved sentences.

    Args:
        description: Raw field description.

    Returns:
        ``None`` when the description does not mention prohibited or reserved
        values. An acknowledgement when every mention is the outside-range
        sentence. A hole or an unrecognised mention is unsupported.
    """
    if _MENTION.search(description) is None:
        return None
    remaining = description
    matched = False
    for pattern in _KNOWN:
        if pattern.search(remaining):
            matched = True
            remaining = pattern.sub("", remaining)
    if matched and _MENTION.search(remaining) is None:
        return OutsideRange(detail="outside the declared range")
    return Unsupported(rule=_RULE, detail="prohibited or reserved text is not outside the declared range")
