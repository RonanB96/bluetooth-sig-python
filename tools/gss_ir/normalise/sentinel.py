"""Sentinel raw values whose meaning is ``not_known`` or ``not_valid``."""

from __future__ import annotations

import re

from tools.gss_ir.v1 import WIRE_SIZE_BYTES, Sentinel, SentinelMeaning, WireType

from .result import Unsupported

_RULE = "sentinel"
_QUOTE_CHARS = "\"'" + "\u201c\u201d\u2018\u2019"
_QUOTED = rf"[{_QUOTE_CHARS}](?P<quoted>.+?)[{_QUOTE_CHARS}]"
_REPRESENTS = re.compile(
    rf"(?P<raw>0x[0-9A-Fa-f]+|\d+)(?![^\n]*?\d[^\n]*?represents)[^\n]*?"
    rf"represents\s*(?:{_QUOTED}|:\s*(?P<bare>[A-Za-z][^.\n]*))",
    re.IGNORECASE,
)
_EQUALS = re.compile(
    r"(?:^|[\s:])(?P<raw>\d+)\s*=\s*(?P<meaning>[A-Za-z][^.\n]*)",
    re.MULTILINE,
)
_BLOCKED = ("nan", "nres", "overflow", "underflow", "greater", "unknown user")


def interpret_raw(value: int, wire: WireType) -> int:
    """Sign-extend a hex bit pattern that names a signed sentinel.

    Args:
        value: Integer parsed from the phrase. Hex is the unsigned bit pattern.
        wire: Field wire type.

    Returns:
        The raw integer stored in the IR. A signed wire type sign-extends a
        value that occupies that width.
    """
    if not wire.value.startswith("sint"):
        return value
    bits = WIRE_SIZE_BYTES[wire] * 8
    span = 1 << bits
    if 0 <= value < span and value >= (1 << (bits - 1)):
        return value - span
    return value


def _meaning(text: str) -> SentinelMeaning | None:
    lowered = " ".join(text.strip().lower().split())
    if any(token in lowered for token in _BLOCKED):
        return None
    if "not known" in lowered or lowered == "unknown":
        return SentinelMeaning.NOT_KNOWN
    if "not valid" in lowered or lowered == "invalid":
        return SentinelMeaning.NOT_VALID
    return None


def _parsed_raw(token: str) -> int:
    if token.lower().startswith("0x"):
        return int(token, 16)
    return int(token)


def parse_sentinels(description: str, wire: WireType) -> tuple[Sentinel, ...] | Unsupported:
    """Parse sentinel phrases.

    Args:
        description: Raw field description.
        wire: Field wire type, used to sign-extend a signed bit pattern.

    Returns:
        Sentinels in phrase order. No sentinel phrase is an empty tuple.
        A recognised phrase whose meaning is outside ``not_known`` and
        ``not_valid`` is unsupported.
    """
    found: list[tuple[int, str]] = []
    for match in _REPRESENTS.finditer(description):
        text = match.group("quoted") if match.group("quoted") is not None else match.group("bare")
        found.append((_parsed_raw(match.group("raw")), text))
    for match in _EQUALS.finditer(description):
        found.append((_parsed_raw(match.group("raw")), match.group("meaning")))
    sentinels: list[Sentinel] = []
    seen: set[int] = set()
    for raw, text in found:
        meaning = _meaning(text)
        if meaning is None:
            return Unsupported(rule=_RULE, detail=f"unsupported sentinel meaning {text.strip()!r}")
        value = interpret_raw(raw, wire)
        if value in seen:
            continue
        seen.add(value)
        sentinels.append(Sentinel(raw_value=value, meaning=meaning))
    return tuple(sentinels)
