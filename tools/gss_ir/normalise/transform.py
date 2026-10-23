"""Parse GSS ``M``, ``d``, and ``b`` as integers.

The handwritten codec evaluates ``raw * coefficient * 10^decimal_exponent * 2^binary_exponent``.
This rule does not fold those integers into a float.
"""

from __future__ import annotations

import re

from tools.gss_ir.v1 import Transform

from .result import Unsupported

_RULE = "transform"
_TRANSFORM = re.compile(
    r"M\s*=\s*(?P<m>[+-]?\s*\d+)\s*,\s*d\s*=\s*(?P<d>[+-]?\s*\d+)\s*"
    r"(?:,\s*and\s*|,\s*|and\s+)b\s*=\s*(?P<b>[+-]?\s*\d+)",
    re.IGNORECASE,
)


def _integer(token: str) -> int:
    return int(token.replace(" ", ""))


def parse_transform(description: str) -> Transform | Unsupported | None:
    """Parse ``M``, ``d``, and ``b``.

    Args:
        description: Raw field description.

    Returns:
        ``None`` when the description has no transform, which means coefficient 1,
        decimal exponent 0, and binary exponent 0. A parsed transform otherwise.
        Malformed transform text is unsupported.
    """
    match = _TRANSFORM.search(description)
    if match is None:
        if re.search(r"\bM\s*=", description):
            return Unsupported(rule=_RULE, detail="transform text is not M, d, and b")
        return None
    return Transform(
        coefficient=_integer(match.group("m")),
        decimal_exponent=_integer(match.group("d")),
        binary_exponent=_integer(match.group("b")),
    )
