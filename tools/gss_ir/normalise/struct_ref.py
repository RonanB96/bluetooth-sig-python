"""Resolve a field that refers to another characteristic."""

from __future__ import annotations

import re

from tools.gss_ir.v1 import IDENTIFIER_PREFIX

from .field_name import parse_field_name
from .result import Unsupported

_RULE = "struct_ref"
_REFERENCE = re.compile(
    r"Refer to .+ characteristic in \\autoref\{sec:"
    r"(org\.bluetooth\.characteristic\.[A-Za-z0-9_.-]+)\}"
)


def parse_struct_reference(description: str) -> str | Unsupported:
    """Read the referenced characteristic identifier.

    Args:
        description: Raw description of a ``struct`` field.

    Returns:
        The referenced identifier, or an unsupported result when the sentence
        does not name one characteristic.
    """
    match = _REFERENCE.fullmatch(description.strip())
    if match is None:
        return Unsupported(rule=_RULE, detail="struct reference does not name a characteristic")
    identifier = match.group(1)
    if not identifier.startswith(IDENTIFIER_PREFIX):
        return Unsupported(rule=_RULE, detail="struct reference does not name a characteristic")
    return identifier


def copied_field_name(field_label: str, referenced_identifier: str) -> str | Unsupported:
    """Name the copied scalar under the referring field.

    A label that ends with the referenced characteristic's short name keeps the
    distinguishing prefix, so ``Minimum Temperature`` copied from Temperature is
    ``minimum``.

    Args:
        field_label: Raw field label on the referring characteristic.
        referenced_identifier: Characteristic whose scalar is copied.

    Returns:
        The IR field name, or the field-name rule's unsupported result.
    """
    parsed = parse_field_name(field_label)
    if isinstance(parsed, Unsupported):
        return parsed
    short = referenced_identifier.removeprefix(IDENTIFIER_PREFIX)
    suffix = f"_{short}"
    if parsed.endswith(suffix) and len(parsed) > len(suffix):
        return parsed[: -len(suffix)]
    return parsed
