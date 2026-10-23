"""Displayed range endpoints converted to raw integers."""

from __future__ import annotations

import re
from fractions import Fraction

from .result import Unsupported

_RULE = "range"
_RANGE = re.compile(
    r"(?:Allowed\s+range\s+is|Range)\s*:?\s*"
    r"(?P<lo>[-+]?\d+(?:\.\d+)?)\s+to\s+"
    r"(?P<hi>[-+]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_MINIMUM = re.compile(r"(?m)^\s*Minimum(?:\s+value)?\s*:\s*(?P<value>[-+]?\d+(?:\.\d+)?)")
_MAXIMUM = re.compile(r"(?m)^\s*Maximum(?:\s+value)?\s*:\s*(?P<value>[-+]?\d+(?:\.\d+)?)")


def round_ties_away_from_zero(value: Fraction) -> int:
    """Round an exact rational to an integer, with ties away from zero.

    Args:
        value: Exact quotient.

    Returns:
        The rounded integer.
    """
    if value.denominator == 1:
        return int(value.numerator)
    negative = value < 0
    absolute = -value if negative else value
    quotient, remainder = divmod(absolute.numerator, absolute.denominator)
    if remainder * 2 >= absolute.denominator:
        quotient += 1
    if negative:
        return -quotient
    return quotient


def displayed_to_raw(token: str, coefficient: int, decimal_exponent: int, binary_exponent: int) -> int:
    """Convert one displayed endpoint to a raw integer.

    Args:
        token: Decimal text, without a trailing sentence mark.
        coefficient: Transform ``M``. Zero is rejected by the caller.
        decimal_exponent: Transform ``d``.
        binary_exponent: Transform ``b``.

    Returns:
        Raw integer, rounded with ties away from zero.
    """
    endpoint = Fraction(token)
    scale = Fraction(coefficient) * (Fraction(10) ** decimal_exponent) * (Fraction(2) ** binary_exponent)
    return round_ties_away_from_zero(endpoint / scale)


def parse_range(
    description: str,
    *,
    coefficient: int,
    decimal_exponent: int,
    binary_exponent: int,
) -> tuple[int, int] | Unsupported:
    """Parse displayed endpoints and store them as raw integers.

    Args:
        description: Raw field description.
        coefficient: Transform ``M``.
        decimal_exponent: Transform ``d``.
        binary_exponent: Transform ``b``.

    Returns:
        Raw minimum and maximum, or an unsupported result when no range is parsed.
    """
    if coefficient == 0:
        return Unsupported(rule="transform", detail="coefficient must not be zero")
    match = _RANGE.search(description)
    if match is not None:
        low = match.group("lo")
        high = match.group("hi")
    else:
        minimum = _MINIMUM.search(description)
        maximum = _MAXIMUM.search(description)
        if minimum is None or maximum is None:
            return Unsupported(rule=_RULE, detail="range is absent")
        low = minimum.group("value")
        high = maximum.group("value")
    return (
        displayed_to_raw(low, coefficient, decimal_exponent, binary_exponent),
        displayed_to_raw(high, coefficient, decimal_exponent, binary_exponent),
    )
