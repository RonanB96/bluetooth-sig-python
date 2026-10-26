"""Characteristics whose unsupported phrase or type appears once.

A missing assigned UUID is included even when two characteristics have no UUID,
because each missing identifier has to stay unresolved.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from ..sources import STRUCT_TYPE, read_characteristic
from .assemble import CHARACTERISTIC_UUID_RULE, iter_characteristic_paths, normalise_path
from .result import Unsupported
from .struct_ref import UNNAMED_REFERENCE
from .wire_type import OUTSIDE_WIRE_PREFIX

_IDENTIFIER = re.compile(r"org\.bluetooth\.[A-Za-z0-9_.-]+")
# Standalone numbers only. ``uint8`` and ``sint16`` stay distinct.
_NUMBER = re.compile(r"(?<![A-Za-z])-?\d+")
_GENERAL_REFERENCE = re.compile(
    r"Refer to .+ characteristic in \\autoref\{sec:org\.bluetooth\.characteristic\.[^}]+\}\.?"
    r"(?:\s+Present if bit \d+ of (?:the )?.+? field is set to [01]\.?)?\Z",
    re.IGNORECASE | re.DOTALL,
)
_FIELD_SECTION = re.compile(
    r"See \\autoref\{sec:org\.bluetooth\.characteristic\.[^/]+/field/[^}]+\}\.?"
    r"(?:\s+Present if bit \d+ of (?:the )?.+? field is set to [01]\.?)?\Z",
    re.IGNORECASE | re.DOTALL,
)


def _collapse(text: str) -> str:
    collapsed = _IDENTIFIER.sub("ID", text)
    return _NUMBER.sub("N", collapsed)


def _signature(result: Unsupported, descriptions: tuple[str, ...]) -> tuple[str, ...]:
    signature = [result.rule, _collapse(result.detail)]
    if result.detail == UNNAMED_REFERENCE:
        for description in descriptions:
            text = description.strip()
            if _GENERAL_REFERENCE.fullmatch(text) is None and _FIELD_SECTION.fullmatch(text) is None:
                signature.append(_collapse(description))
    if result.detail.startswith(OUTSIDE_WIRE_PREFIX):
        signature.extend(_collapse(description) for description in descriptions)
    return tuple(signature)


def special_cases(root: Path | None = None) -> tuple[dict[str, str], ...]:
    """Return the deferred one-off characteristics in identifier order.

    Args:
        root: Repository root. Defaults to the root that contains this package.

    Returns:
        Records with ``identifier``, ``rule``, and ``detail``.
    """
    grouped: dict[tuple[str, ...], list[tuple[str, Unsupported]]] = defaultdict(list)
    for path in iter_characteristic_paths(root):
        result = normalise_path(path, root=root)
        if not isinstance(result, Unsupported):
            continue
        characteristic = read_characteristic(path, source_path=path.name)
        outside_wire = result.detail.startswith(OUTSIDE_WIRE_PREFIX)
        descriptions = tuple(
            field.description for field in characteristic.fields if field.type_text == STRUCT_TYPE or outside_wire
        )
        grouped[_signature(result, descriptions)].append((path.stem, result))
    records: list[dict[str, str]] = []
    for items in grouped.values():
        if len(items) != 1 and items[0][1].rule != CHARACTERISTIC_UUID_RULE:
            continue
        for identifier, result in items:
            records.append(
                {
                    "identifier": identifier,
                    "rule": result.rule,
                    "detail": result.detail,
                }
            )
    return tuple(sorted(records, key=lambda item: item["identifier"]))
