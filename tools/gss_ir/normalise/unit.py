"""Join an ``org.bluetooth.unit.*`` identifier to its assigned number."""

from __future__ import annotations

import re
from collections.abc import Mapping

from tools.gss_ir.v1 import UNIT_PREFIX, UnitRef

from .result import Unsupported

_RULE = "unit"
_UNIT = re.compile(r"org\.bluetooth\.unit\.([A-Za-z0-9_.]+)")


def parse_unit(description: str, units: Mapping[str, int]) -> UnitRef | Unsupported | None:
    """Extract a unit identifier and join its 16-bit UUID.

    Args:
        description: Raw field description.
        units: Assigned unit numbers keyed by the full unit identifier.

    Returns:
        ``None`` when the description names no unit. The joined unit, or an
        unsupported result when the identifier has no assigned number.
    """
    normalised = re.sub(r"org\.bluetooth\.unit\.\s*", "org.bluetooth.unit.", description)
    match = _UNIT.search(normalised)
    if match is None:
        return None
    identifier = f"{UNIT_PREFIX}{match.group(1).rstrip('.')}"
    uuid = units.get(identifier)
    if uuid is None:
        return Unsupported(rule=_RULE, detail=f"unknown unit {identifier}")
    return UnitRef(identifier=identifier, uuid=uuid)
